# -*- coding: utf-8 -*-
"""The expert rating instrument: one short bilingual form per procedure.

The quantitative analyses in this package answer "how far is the plan from the
ground truth, in millimetres". They cannot answer "would a surgeon use it".
Those are different questions, and the second one has no ground truth on disk:
a 0.8 mm orbital error is excellent or unremarkable depending on where the
0.8 mm sits, and a screw 1 mm outside a pedicle is a footnote laterally and a
reoperation medially. So each procedure gets a small panel-rated form whose
questions are the things that decide acceptability *in that operation*.

The module has one audience-driven split, and it is the whole design:

- **What a rater reads is bilingual and short** -- a dimension and a question,
  nothing else. The form is a data-collection sheet, not a lesson: a surgeon
  should be able to fill one in without reading anything first.
- **What a developer reads is English and lives in the generated document**
  (beside the workbook, in Experiments/0_QualitativeEvaluation/) -- why each
  question is there, what a 5 means,
  which metric it sits beside, the protocol and the analysis plan. Keeping it out
  of the form is what makes the form short; keeping it in this module is what
  keeps it from drifting away from the questions it explains.

Two rules shape the question sets themselves. A form asks **six to eight
detailed questions about that operation**, and then the same **two closing
questions** on every one of the eight -- is the plan safe, and would you use it.
The detailed questions come first on purpose: a rater asked "would you use this"
before looking at anything answers on impression, while the same person asked
after eight specific questions answers on what they have just found. A detailed
question earns its place only if a surgeon would refuse or revise a plan because
of it, and if the existing metrics cannot already see it.

Qt-free and Slicer-free, so scripts/build_likert_forms.py runs it outside Slicer.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Sequence, Tuple

# ---------------------------------------------------------------------------
# What a rater is told, which is as little as possible
# ---------------------------------------------------------------------------

#: Five points, not seven: five is about the granularity a surgeon can apply
#: reproducibly to somebody else's plan. The analysis treats it as ordinal
#: either way, so the extra points buy nothing.
FORM_INSTRUCTIONS = [
    ("Score every row: 5 = strongly agree, 4 = agree, 3 = unsure, "
     "2 = disagree, 1 = strongly disagree. Write NA if you cannot tell from "
     "what you were shown.",
     "每行评分：5＝完全同意，4＝同意，3＝不确定，2＝不同意，1＝完全不同意；"
     "若从所给资料无法判断，请填 NA。"),
    ("If a question covers several implants / screws / bone segments, score the "
     "worst one and say which in the comment.",
     "若某一问题涉及多枚种植体／螺钉／骨段，请按最差的一个评分，并在备注中注明是哪一个。"),
]

#: The rows a rater fills in before scoring. Deliberately three: anything more
#: is a form the panel has to be walked through.
HEADER_FIELDS = [
    ("Rater", "评分者"),
    ("Case ID", "病例编号"),
    ("Date", "日期"),
]

FORM_COLUMNS = ["No.", "Question (English)", "问题（中文）", "Score / 评分",
                "Comment / 备注"]

#: The two questions that produce the qualitative material proper. The failure
#: modes a panel writes in these are what tell you what to fix; the numbers only
#: tell you whether something is wrong.
FREE_TEXT = [
    ("If you scored anything 3 or below, what is wrong with the plan?",
     "若有条目评分≤3，请说明该规划的问题所在。"),
    ("Anything else you would want changed or checked before surgery?",
     "术前还有什么你希望修改或核实的？"),
]

#: The two questions carrying their own scale print it inside the question, so
#: the form needs no legend and no cross-reference to another sheet.
SCALE_A = "agreement 1-5"
SCALE_B = "acceptability 1-5"
SCALE_C = "pairwise -2..+2"

# ---------------------------------------------------------------------------
# The three core questions, present in every task
# ---------------------------------------------------------------------------
#
# question_en / question_zh are what the rater sees. anchor5, why and quant are
# for the developer document and never reach the form.

CORE_ITEMS = [
    {
        "id": "G1",
        "scale": SCALE_A,
        "dimension_en": "Safety",
        "dimension_zh": "安全性",
        "question_en": "The plan is safe: no critical structure is put at risk.",
        "question_zh": "该规划是安全的：未危及任何重要解剖结构。",
        "anchor5": "Every structure at risk is cleared by a margin you would "
                   "accept without re-checking intra-operatively.",
        "why": "Asked last and asked once, as a whole-plan judgement: the "
               "detailed questions name the structures one at a time, and this "
               "one asks whether anything anywhere would stop you. It is also "
               "the only question a single rater's low score may veto a case "
               "on, and the one the geometric metrics cannot express - the same "
               "millimetre is trivial in one direction and a reoperation in "
               "another.",
        "quant": "None. Surface distances are unsigned and structure-blind.",
    },
    {
        "id": "G2",
        "scale": SCALE_B,
        "dimension_en": "Overall acceptability (primary endpoint)",
        "dimension_zh": "总体可接受性（主要终点）",
        "question_en": "Overall, would you use this plan for this patient?  "
                       "(5 = use as planned · 4 = use after a trivial tweak · "
                       "3 = re-plan one part · 2 = major re-plan · 1 = discard)",
        "question_zh": "总体而言，你会为这位患者使用这份规划吗？"
                       "（5＝可直接使用；4＝微调后使用；3＝需重新规划其中一部分；"
                       "2＝需大幅重新规划；1＝废弃）",
        "anchor5": "Use as planned, no modification.",
        "why": "The endpoint the paper reports: the share of plans a surgeon "
               "would use without re-planning (>= 4). Phrased as a decision "
               "rather than as agreement, because 'acceptable' on its own means "
               "whatever each rater takes it to mean. Asked after the detailed "
               "questions, so it is a verdict on a plan the rater has just "
               "examined rather than a first impression.",
        "quant": "The variable every geometric metric is validated against "
                 "(Spearman rho, and an ROC-derived clinical threshold).",
    },
]

PAIRWISE_ITEM = {
    "id": "PW",
    "scale": SCALE_C,
    "dimension_en": "Which plan is better",
    "dimension_zh": "哪一份规划更好",
    "question_en": "Two plans for this patient are shown as A and B. Which would "
                   "you take into theatre?  (+2 = A much better · +1 = A "
                   "slightly better · 0 = equivalent · -1 = B slightly better · "
                   "-2 = B much better)",
    "question_zh": "本例给出A、B两份规划。你会把哪一份带入手术室？"
                   "（+2＝A明显更优；+1＝A略优；0＝两者相当；−1＝B略优；−2＝B明显更优）",
    "anchor5": "0 is a real answer: 'equivalent' is the result this study is "
               "looking for, not a failure to decide.",
    "why": "Turns acceptability into a comparison against current practice, "
           "which is the claim a reviewer will ask for.",
    "quant": "The qualitative counterpart of beats_manual / delta_gain.",
}

# ---------------------------------------------------------------------------
# The eight procedures
# ---------------------------------------------------------------------------
#
# runs_available is what is on disk under Experiments/<Extension>/
# Overall_Performance today; sample_n is what the panel is asked to rate.

TASKS: List[Dict[str, Any]] = [
    {
        "task_id": "T1",
        "sheet": "T1_Zygomatic",
        "extension": "ZygomaticImplantPlanner",
        "title_en": "Zygomatic implant planning",
        "title_zh": "颧骨种植体规划",
        "unit": "One maxilla with all its planned implants (worst implant).",
        "materials": "3D skull with the implant rods and the sinuses; one curved "
                     "reformat along each implant; coronal and axial at the "
                     "zygomatic body; occlusal view of the emergence points.",
        "comparator": "Yes - the surgeon's own implant plan (Implant_1..N STL) "
                      "is stored for every case.",
        "runs_available": 29,
        "sample_n": 20,
        "quant": "Relative BIC per path, per-side sum, beats_manual.",
        "gap": "BIC scores bone along the rod and nothing else: it is blind to "
               "where the head emerges, to the orbit, and to whether the "
               "implants together can carry a prosthesis.",
        "items": [
            {
                "id": "Z1",
                "scale": SCALE_A,
                "dimension_en": "Bone engagement",
                "dimension_zh": "骨内接合",
                "question_en": "Each implant engages enough zygomatic bone along its "
                               "course for primary stability",
                "question_zh": "每枚种植体沿其路径获得足够的颧骨骨量，可取得初期稳定性",
                "anchor5": "Full-thickness engagement of the zygomatic body on every "
                           "implant; you would expect >35 Ncm.",
                "why": "Primary stability decides immediate loading, the whole "
                       "point of the technique. Across the 116 saved paths 28% "
                       "engage LESS bone than the surgeon's own implant on the "
                       "same entry, and the posterior-left implant accounts for "
                       "15 of those.",
                "quant": "relative_bic (median 1.18; 33 of 116 paths below 1.00).",
            },
            {
                "id": "Z2",
                "scale": SCALE_A,
                "dimension_en": "Implant length",
                "dimension_zh": "种植体长度",
                "question_en": "The length chosen for each implant is right - long "
                               "enough to engage the zygoma, not so long that the apex "
                               "pushes through",
                "question_zh": "每枚种植体所选长度恰当——既足以锚固于颧骨，又不致因过长而穿出",
                "anchor5": "The length you would have picked from the same catalogue "
                           "for that trajectory.",
                "why": "Length is chosen from a fixed catalogue, and these runs "
                       "sit at the 52.5 mm maximum in 47% of paths: 36 of 116 "
                       "are more than 2 mm longer than the surgeon's choice and "
                       "15 more than 2 mm shorter. A length metric alone cannot "
                       "say which way is wrong.",
                "quant": "length_ours_mm vs length_manual_mm (47% at the catalogue "
                         "maximum).",
            },
            {
                "id": "Z3",
                "scale": SCALE_A,
                "dimension_en": "Apex position",
                "dimension_zh": "尖端位置",
                "question_en": "The apex of each implant stops inside the zygomatic "
                               "body, short of the orbital floor and the infratemporal "
                               "fossa",
                "question_zh": "每枚种植体的尖端止于颧骨体内，未进入眶底，也未穿入颞下窝",
                "anchor5": "Every apex is surrounded by bone, with a margin you "
                           "would not re-check intra-operatively.",
                "why": "The two catastrophic exits of this operation, and the "
                       "one the length findings point at: BIC integrates bone "
                       "along the rod and cannot say which side of the bone the "
                       "tip came out of.",
                "quant": "Not measured anywhere.",
            },
            {
                "id": "Z4",
                "scale": SCALE_A,
                "dimension_en": "Sinus course",
                "dimension_zh": "与上颌窦的关系",
                "question_en": "The course of each implant relative to the sinus wall "
                               "suits this patient's anatomy",
                "question_zh": "每枚种植体相对上颌窦壁的走行符合该患者的解剖",
                "anchor5": "The course matches the ZAGA type you would have chosen "
                           "from the same anatomy.",
                "why": "The single decision that separates a modern zygomatic "
                       "plan from a bad one, and a judgement about wall contact "
                       "that no distance captures.",
                "quant": "Not measured anywhere.",
            },
            {
                "id": "Z5",
                "scale": SCALE_A,
                "dimension_en": "Prosthetic emergence",
                "dimension_zh": "修复穿出位置",
                "question_en": "The implant heads emerge where a screw-retained "
                               "full-arch prosthesis can use them",
                "question_zh": "种植体头部的穿出位置可供螺丝固位全牙弓修复体使用",
                "anchor5": "Crestal or slightly palatal emergence, angulation "
                           "correctable with a standard multi-unit abutment.",
                "why": "A zygomatic implant is placed for a prosthesis. Perfect "
                       "bone engagement with a palatal emergence 8 mm off the "
                       "arch is a failed plan.",
                "quant": "Not measured anywhere.",
            },
            {
                "id": "Z6",
                "scale": SCALE_A,
                "dimension_en": "Distribution",
                "dimension_zh": "分布",
                "question_en": "The four implants are well spread along the arch and do "
                               "not converge into each other",
                "question_zh": "四枚种植体沿牙弓分布合理，且彼此不汇聚碰撞",
                "anchor5": "Even anteroposterior spread, no two implants converging "
                           "toward contact.",
                "why": "Every metric here is per implant, and all four can be "
                       "individually good while the quad construct as a whole "
                       "cannot carry a bridge. The per-side totals are the only "
                       "hint of it.",
                "quant": "Complements sum_relative_bic per side.",
            },
            {
                "id": "Z7",
                "scale": SCALE_A,
                "dimension_en": "Surgical access",
                "dimension_zh": "手术可达性",
                "question_en": "Each trajectory can be reached and drilled through a "
                               "standard intraoral approach with zygomatic "
                               "instrumentation",
                "question_zh": "每条规划路径均可经标准口内入路、使用颧骨种植器械到达并完成备洞",
                "anchor5": "You could drill every implant as drawn, without a "
                           "further window or a second approach.",
                "why": "The concrete form of 'can this be carried out'. A "
                       "trajectory that is optimal and unreachable is not a "
                       "plan, and nothing upstream tests reachability.",
                "quant": "Not measured anywhere.",
            },
        ],
    },
    {
        "task_id": "T2",
        "sheet": "T2_Orbital",
        "extension": "OrbitalFractureReconstruction",
        "title_en": "Orbital wall fracture reconstruction",
        "title_zh": "眶壁骨折重建",
        "unit": "One fractured orbit.",
        "materials": "3D of the reconstructed surface in the skull; coronal "
                     "series through the defect (anterior, mid, posterior); "
                     "sagittal through the floor; mirrored healthy orbit "
                     "overlaid.",
        "comparator": "Reference anatomy only (the surgeon-labelled correct "
                      "orbital volume), which is not a competing plan - no "
                      "pairwise question.",
        "runs_available": 30,
        "sample_n": 20,
        "quant": "ASSD, HD95, within-1/2 mm share, volume ratio, and the "
                 "fractured-vs-reconstructed improvement pairing.",
        "gap": "Surface distance is averaged over the whole orbit, where "
               "millimetres at the posterior ledge decide enophthalmos and "
               "millimetres at the rim decide nothing.",
        "items": [
            {
                "id": "O1",
                "scale": SCALE_A,
                "dimension_en": "Correct side and alignment",
                "dimension_zh": "侧别与对位",
                "question_en": "The reconstruction is on the fractured orbit and the "
                               "mirrored healthy orbit is correctly aligned to it",
                "question_zh": "重建位于骨折侧眼眶，且镜像健侧眶的对位正确",
                "anchor5": "Right side, and the mirrored template sits on the "
                           "fracture without a visible offset or tilt.",
                "why": "The plan is built by mirroring the healthy orbit, and "
                       "the side is chosen from a control whose two options are "
                       "coloured boxes rather than left and right. Getting it "
                       "wrong reconstructs the healthy orbit and every distance "
                       "still comes out plausible.",
                "quant": "centroid_gap_mm would move, but nothing states the side.",
            },
            {
                "id": "O2",
                "scale": SCALE_A,
                "dimension_en": "Defect coverage",
                "dimension_zh": "缺损覆盖",
                "question_en": "The reconstruction covers the whole defect and rests on "
                               "intact bone all round",
                "question_zh": "重建覆盖整个缺损，四周均支撑于完整骨质之上",
                "anchor5": "Continuous coverage with an overlap onto intact bone on "
                           "every edge.",
                "why": "An uncovered corner lets orbital content herniate again; "
                       "it is a small share of the surface, so a mean distance "
                       "cannot see it.",
                "quant": "Partly in within_1mm_pct (62-90% of the surface over "
                         "these 30 cases).",
            },
            {
                "id": "O3",
                "scale": SCALE_A,
                "dimension_en": "Posterior ledge",
                "dimension_zh": "后部骨性支撑",
                "question_en": "The posterior edge of the defect is covered and "
                               "supported by stable bone",
                "question_zh": "缺损后缘已被覆盖，并有稳定骨质支撑",
                "anchor5": "The posterior defect edge is bridged and the implant "
                           "would rest on stable posterior bone.",
                "why": "Where reconstructions fail and where late enophthalmos "
                       "comes from, and a tiny share of the surface, so ASSD "
                       "(0.50-1.24 mm here) cannot see it.",
                "quant": "Invisible to assd_mm; partly visible in hd95_mm (1.5-5.5 "
                         "mm).",
            },
            {
                "id": "O4",
                "scale": SCALE_A,
                "dimension_en": "Orbital contour",
                "dimension_zh": "眶壁形态",
                "question_en": "The floor reproduces the normal S-shaped contour with "
                               "its post-bulge, not a flat plate",
                "question_zh": "眶底再现正常的“S”形轮廓及球后隆起，而非平坦的板状",
                "anchor5": "The post-bulge is present and in the right "
                           "anteroposterior position.",
                "why": "A flattened floor gives correct volume and wrong globe "
                       "position, and a volume ratio passes it.",
                "quant": "Complements volume_ratio, which a flat plate passes.",
            },
            {
                "id": "O5",
                "scale": SCALE_A,
                "dimension_en": "Orbital volume",
                "dimension_zh": "眶容积",
                "question_en": "Orbital volume matches the healthy side - neither "
                               "under-corrected nor over-filled",
                "question_zh": "眶容积与健侧相当——既非矫正不足，也非过度填充",
                "anchor5": "You would predict neither enophthalmos nor proptosis or "
                           "restricted motility.",
                "why": "These runs OVER-fill: 20 of 30 reconstructions exceed "
                       "the correct volume by more than 5%, median +9% and up to "
                       "+49%. An over-filled orbit pushes the globe forward and "
                       "tethers the muscles, which is why the question names "
                       "both directions rather than enophthalmos alone.",
                "quant": "volume_ratio (0.76 to 1.49 over the cohort, median "
                         "1.09).",
            },
            {
                "id": "O6",
                "scale": SCALE_A,
                "dimension_en": "Posterior limit",
                "dimension_zh": "后界安全",
                "question_en": "The posterior edge stops at a safe distance from the "
                               "orbital apex and the optic canal",
                "question_zh": "后缘与眶尖及视神经管保持安全距离",
                "anchor5": "You would place this implant without fearing the apex.",
                "why": "The complication that costs sight, decided by where the "
                       "reconstruction ENDS - which no overlap or mean-distance "
                       "measure reports.",
                "quant": "Not measured anywhere.",
            },
            {
                "id": "O7",
                "scale": SCALE_A,
                "dimension_en": "Seat and fixation",
                "dimension_zh": "支撑与固定",
                "question_en": "There is a stable seat at the orbital rim where the "
                               "implant can be fixed",
                "question_zh": "眶缘处有稳定的支撑位置，可供植入物固定",
                "anchor5": "A flat anterior seat on intact rim, enough for a screw.",
                "why": "An unfixed orbital implant migrates, and migration "
                       "reproduces the deformity the operation corrected.",
                "quant": "Not measured anywhere.",
            },
            {
                "id": "O8",
                "scale": SCALE_A,
                "dimension_en": "Realisability",
                "dimension_zh": "可制作与植入",
                "question_en": "This shape could be made as an orbital plate and "
                               "inserted through a standard approach",
                "question_zh": "该形状可制成眶板，并经标准入路植入",
                "anchor5": "Manufacturable and insertable with no shape feature that "
                           "would have to be trimmed away.",
                "why": "An orbital reconstruction that cannot be slid in through "
                       "a 20 mm incision is an anatomical model, not a plan.",
                "quant": "Not measured anywhere.",
            },
        ],
    },
    {
        "task_id": "T3",
        "sheet": "T3_Shoulder",
        "extension": "ReverseShoulderArthroplasty",
        "title_en": "Reverse shoulder arthroplasty - baseplate screws",
        "title_zh": "反式全肩关节置换——基座螺钉",
        "unit": "One shoulder, baseplate and its screws (worst screw).",
        "materials": "3D scapula with baseplate and screws from lateral and "
                     "posterior; one reformat along each screw; axial at the "
                     "glenoid showing version.",
        "comparator": "Yes - the surgeon's own screw plan (Manual_Screw_Model_* "
                      "and RSA_ManualPlanResults.tsv), from the same baseplate "
                      "pose.",
        "runs_available": 60,
        "sample_n": 20,
        "quant": "theta1/2/3, delta (bone-density integral over the cone), "
                 "delta_gain against the manual plan.",
        "gap": "Delta rewards density and nothing else. It cannot see the "
               "suprascapular notch, the joint line, or whether a screw is long "
               "enough to be worth placing.",
        "items": [
            {
                "id": "R1",
                "scale": SCALE_A,
                "dimension_en": "Baseplate position",
                "dimension_zh": "基座位置",
                "question_en": "The baseplate position, version and inclination are what "
                               "I would have chosen for this glenoid",
                "question_zh": "基座的位置、倾角与仰角与我对该肩胛盂本会选择的一致",
                "anchor5": "The baseplate you would have placed yourself, including "
                           "its inferior position and tilt.",
                "why": "Every screw is planned inside this pose, and the pose is "
                       "set from a single fiducial. If it is wrong, perfect "
                       "screws are worthless - and no number in the workbook "
                       "judges it.",
                "quant": "Not measured; the baseplate pose is an input to every "
                         "other number.",
            },
            {
                "id": "R2",
                "scale": SCALE_A,
                "dimension_en": "Baseplate seating",
                "dimension_zh": "基座就位",
                "question_en": "The baseplate has adequate backside contact with the "
                               "glenoid, without unintended overhang beyond the rim",
                "question_zh": "基座背面与肩胛盂接触充分，且无非计划的超出盂缘的悬空",
                "anchor5": "Full backside contact on reamed bone, with only the "
                           "intended inferior overhang.",
                "why": "Backside contact is what prevents micromotion and "
                       "loosening; a density integral along a screw says nothing "
                       "about it.",
                "quant": "Not measured anywhere.",
            },
            {
                "id": "R3",
                "scale": SCALE_A,
                "dimension_en": "Central fixation",
                "dimension_zh": "中央固定",
                "question_en": "The central peg or screw sits in the best available bone "
                               "and to an appropriate depth",
                "question_zh": "中央柱或中央螺钉位于可用的最佳骨质中，且深度适当",
                "anchor5": "Central fixation into the scapular pillar with the depth "
                           "you would choose.",
                "why": "The central peg is the primary stabiliser of a reverse "
                       "baseplate, and the analysis scores only the two "
                       "peripheral screws.",
                "quant": "peg_integral is recorded but never scored.",
            },
            {
                "id": "R4",
                "scale": SCALE_A,
                "dimension_en": "Screw containment",
                "dimension_zh": "螺钉包容",
                "question_en": "Each screw stays within bone along its length, or exits "
                               "only where you would accept it",
                "question_zh": "每枚螺钉全长位于骨内，或仅在你可接受之处穿出",
                "anchor5": "Both screws contained, or a protrusion you would not act "
                           "on.",
                "why": "27% of the screws in these runs are BEST EFFORT rows - "
                       "the optimiser found no trajectory in the whole cone that "
                       "kept the screw inside the bone, and returned the "
                       "deepest-reaching one instead. That screw was never "
                       "optimised for anything a density score reports.",
                "quant": "selection == 'best effort' (33 of 120 screws).",
            },
            {
                "id": "R5",
                "scale": SCALE_A,
                "dimension_en": "Bone purchase",
                "dimension_zh": "骨把持力",
                "question_en": "Each screw runs in dense bone for long enough to hold "
                               "the baseplate",
                "question_zh": "每枚螺钉在致密骨内走行足够长度，足以固定基座",
                "anchor5": "Every screw is in a named dense column - spine, lateral "
                           "pillar, coracoid base - over most of its length.",
                "why": "Baseplate loosening is the failure mode of this "
                       "operation. On the 87 properly planned screws the "
                       "pipeline finds denser bone than the surgeon 62% of the "
                       "time and less dense 38%, so this is not a settled "
                       "question.",
                "quant": "delta / delta_gain (pipeline denser in 54 of 87).",
            },
            {
                "id": "R6",
                "scale": SCALE_A,
                "dimension_en": "Construct stability",
                "dimension_zh": "构型稳定性",
                "question_en": "The screws diverge enough from each other to make a "
                               "mechanically stable construct",
                "question_zh": "各螺钉之间发散充分，形成力学稳定的固定构型",
                "anchor5": "Clear divergence in both planes; no two screws "
                           "effectively parallel.",
                "why": "theta is recorded (median 14.5 degrees, some screws "
                       "sitting exactly on the 22.5 degree cone limit) but has "
                       "no clinical cut-off; only a surgeon can say whether this "
                       "triangle is stable.",
                "quant": "theta1/2/3 gain their clinical reading here.",
            },
            {
                "id": "R7",
                "scale": SCALE_A,
                "dimension_en": "Implantable",
                "dimension_zh": "可植入性",
                "question_en": "This construct can be implanted through a standard "
                               "approach with the instruments and implant sizes "
                               "available to me",
                "question_zh": "该固定构型可经标准入路、使用我现有的器械与假体型号完成植入",
                "anchor5": "You could implant it as drawn, with the screw lengths "
                           "and angles your system offers.",
                "why": "The concrete form of 'can this be carried out': a "
                       "trajectory your screwdriver cannot reach is a drawing, "
                       "not a plan. Pipeline and surgeon trajectories differ by "
                       "up to 22 degrees and their tips by up to 15 mm, so the "
                       "two plans are not interchangeable in the hand.",
                "quant": "plans_apart_deg (median 6.8, max 22.4); tip_gap_mm "
                         "(median 4.6, max 15.2).",
            },
        ],
    },
    {
        "task_id": "T4",
        "sheet": "T4_Cranial",
        "extension": "CranialImplantPlanning",
        "title_en": "Cranial implant planning (cranioplasty)",
        "title_zh": "颅骨缺损修补体规划",
        "unit": "One defect and its implant.",
        "materials": "3D skull with the implant in place and with it hidden; "
                     "three orthogonal slices through the margin; mirrored "
                     "contralateral contour overlaid.",
        "comparator": "Reference anatomy (the challenge ground truth = the "
                      "removed bone flap). Pairwise only if a commercial or "
                      "manual design is available.",
        "runs_available": 100,
        "sample_n": 25,
        "quant": "DSC, bDSC, HD95, coverage and false-positive area shares.",
        "gap": "DSC against the removed flap says nothing about how the head "
               "will look, which is what the operation is for; and a plan can "
               "score well while being unfixable or too thin to mill.",
        "items": [
            {
                "id": "C1",
                "scale": SCALE_A,
                "dimension_en": "Skull model",
                "dimension_zh": "颅骨模型",
                "question_en": "The skull model the implant was built on is correct at "
                               "the defect edge - no missing bone, no soft tissue "
                               "included",
                "question_zh": "用于生成修补体的颅骨模型在缺损边缘是正确的——既无骨质缺失，也未纳入软组织",
                "anchor5": "The bone surface around the defect is the patient's "
                           "bone, with thin bone present and nothing soft included.",
                "why": "The implant margin is fitted to a thresholded skull, so "
                       "a threshold that drops thin temporal bone or keeps dura "
                       "moves the margin without any implant metric noticing. "
                       "The segmentation itself is scored nowhere.",
                "quant": "Not measured anywhere; only the implant is scored.",
            },
            {
                "id": "C2",
                "scale": SCALE_A,
                "dimension_en": "Defect coverage",
                "dimension_zh": "缺损覆盖",
                "question_en": "The implant closes the whole defect - no part of the "
                               "defect is left open",
                "question_zh": "修补体封闭了整个缺损——缺损区无遗留未覆盖之处",
                "anchor5": "Complete closure, with no residual opening you would "
                           "have to fill separately.",
                "why": "The commonest real failure in these runs: in the worst "
                       "eight cases the implant covers 69-80% of the defect "
                       "while DSC still reads 0.73-0.87, because a global "
                       "overlap score cannot see which part is missing.",
                "quant": "gt_covered_2mm_pct (median 94%, worst 69%).",
            },
            {
                "id": "C3",
                "scale": SCALE_A,
                "dimension_en": "Extent onto intact bone",
                "dimension_zh": "对完整骨质的侵占",
                "question_en": "The implant stops at the defect edge and does not sit on "
                               "or extend over intact skull",
                "question_zh": "修补体止于缺损边缘，未覆盖或超出到完整颅骨之上",
                "anchor5": "The implant ends where the bone begins, all the way "
                           "round.",
                "why": "The mirror error of coverage, and it is the one that "
                       "costs healthy bone: an implant overlapping intact skull "
                       "either sits proud or has to be trimmed in theatre. Eight "
                       "of these runs overlap on 15-31% of the implant surface.",
                "quant": "implant_on_gt_2mm_pct (median 96%, worst 69%).",
            },
            {
                "id": "C4",
                "scale": SCALE_A,
                "dimension_en": "Margin fit",
                "dimension_zh": "边缘吻合",
                "question_en": "At the defect edge the implant is flush with the bone - "
                               "no gap and no step",
                "question_zh": "在缺损边缘，修补体与骨面平齐——无间隙、无台阶",
                "anchor5": "A continuous, flush margin all the way round.",
                "why": "The first thing a surgeon checks in theatre, and a 1 mm "
                       "gap invisible in a whole-implant DSC is a palpable ridge "
                       "under a thin scalp.",
                "quant": "Complements bdsc (the border band).",
            },
            {
                "id": "C5",
                "scale": SCALE_A,
                "dimension_en": "Contour and symmetry",
                "dimension_zh": "外形与对称",
                "question_en": "The outer contour restores the skull shape and is "
                               "symmetric with the other side",
                "question_zh": "外表面恢复颅骨外形，并与对侧对称",
                "anchor5": "You could not tell from the outside that this skull had "
                           "a defect.",
                "why": "Cosmesis is the indication for most cranioplasties, and "
                       "is not what DSC measures.",
                "quant": "Not measured; DSC scores volume overlap, not shape as "
                         "seen.",
            },
            {
                "id": "C6",
                "scale": SCALE_A,
                "dimension_en": "Inner surface",
                "dimension_zh": "内表面",
                "question_en": "The inner surface does not press into the intracranial "
                               "space",
                "question_zh": "内表面未向内侵占颅内空间",
                "anchor5": "No inward protrusion anywhere; the inner surface follows "
                           "the inner table.",
                "why": "The complication that turns a cosmetic operation into a "
                       "neurological one, and an unsigned metric treats 2 mm "
                       "inward exactly like 2 mm outward.",
                "quant": "Invisible to DSC/HD95, which are unsigned.",
            },
            {
                "id": "C7",
                "scale": SCALE_A,
                "dimension_en": "Thickness",
                "dimension_zh": "厚度",
                "question_en": "Implant thickness matches the surrounding skull - "
                               "nowhere thin enough to be weak, nowhere thick enough to "
                               "be felt",
                "question_zh": "修补体厚度与周围颅骨相当——既无薄弱之处，也无可触及的过厚之处",
                "anchor5": "Thickness follows the neighbouring bone across the whole "
                           "implant.",
                "why": "Implant volume runs from 0.70 to 1.44 times the correct "
                       "volume across these runs while DSC stays respectable, "
                       "because a volume overlap score is indifferent to where "
                       "the volume sits.",
                "quant": "volume_ratio (0.70 to 1.44 over the cohort).",
            },
            {
                "id": "C8",
                "scale": SCALE_A,
                "dimension_en": "A clean single piece",
                "dimension_zh": "成形质量",
                "question_en": "The implant is one clean piece - no spikes, stray "
                               "fragments, holes or ragged edges",
                "question_zh": "修补体为完整干净的一块——无尖刺、无游离碎块、无孔洞、无锯齿状边缘",
                "anchor5": "A smooth, closed shell you could hand to the scrub nurse "
                           "as it is.",
                "why": "Several runs pair a good HD95 of 2-4 mm with a single "
                       "protrusion 25-52 mm away: a 95th percentile is designed "
                       "not to see one spur, and a spur is the defect a surgeon "
                       "spots instantly.",
                "quant": "hd_max_mm is the only trace of it, and it is never "
                         "quoted.",
            },
        ],
    },
    {
        "task_id": "T5",
        "sheet": "T5_Pelvic",
        "extension": "PelvicFracturePlanning",
        "title_en": "Pelvic fracture reduction planning",
        "title_zh": "骨盆骨折复位规划",
        "unit": "One pelvis with all reduced fragments (worst fragment).",
        "materials": "3D of the reduced pelvis from front, inlet and outlet; the "
                     "injured hemipelvis mirrored onto the intact one; axial and "
                     "coronal through the acetabulum.",
        "comparator": "Yes - the surgeon's own annotated reduction is recorded "
                      "for every annotated piece.",
        "runs_available": 77,
        "sample_n": 20,
        "quant": "Displacement mm, rotation deg, point error over the fragment "
                 "surface, read from the recorded transform.",
        "gap": "The recorded transform is exact and clinically mute: it cannot "
               "say whether the residual is at the acetabular dome or the iliac "
               "wing, and those differ by a hip replacement.",
        "items": [
            {
                "id": "P1",
                "scale": SCALE_A,
                "dimension_en": "Sacroiliac joint",
                "dimension_zh": "骶髂关节",
                "question_en": "The sacroiliac joint is reduced and congruent",
                "question_zh": "骶髂关节已复位且对合一致",
                "anchor5": "A congruent SI joint with no residual diastasis or step.",
                "why": "The articular surface these cases actually contain: "
                       "every scored piece is an ilium or a sacrum, so the SI "
                       "joint is where a millimetre matters. Piece displacement "
                       "runs to 11.8 mm and rotation to 13.4 degrees across the "
                       "cohort.",
                "quant": "Localises displacement_mm (median 1.7, max 11.8).",
            },
            {
                "id": "P2",
                "scale": SCALE_A,
                "dimension_en": "Sacral fracture and foramina",
                "dimension_zh": "骶骨骨折与骶孔",
                "question_en": "Where the sacrum is fractured, it is reduced without a "
                               "step across a neural foramen (leave blank if the sacrum "
                               "is intact)",
                "question_zh": "若骶骨骨折，复位后未在骶孔处遗留台阶（骶骨完整请留空）",
                "anchor5": "The foraminal lines are continuous and the roots are not "
                           "narrowed.",
                "why": "A quarter of the scored pieces in these runs are sacral. "
                       "A step at a transforaminal fracture compresses the "
                       "sacral roots, and a rigid-body error over the whole "
                       "sacrum reports it as a millimetre or two.",
                "quant": "Not localised; displacement_mm is measured at one "
                         "reference point.",
            },
            {
                "id": "P3",
                "scale": SCALE_A,
                "dimension_en": "Cortical continuity",
                "dimension_zh": "皮质连续性",
                "question_en": "The main fracture lines show continuous cortex",
                "question_zh": "主要骨折线处皮质连续",
                "anchor5": "The lines you read on a postoperative film - arcuate, "
                           "iliopectineal - are continuous.",
                "why": "How reduction is actually judged intra-operatively and "
                       "on follow-up films; it is a line, not a volume.",
                "quant": "Not measured anywhere.",
            },
            {
                "id": "P4",
                "scale": SCALE_A,
                "dimension_en": "Ring symmetry",
                "dimension_zh": "骨盆环对称",
                "question_en": "The pelvic ring is symmetric with the uninjured side - "
                               "no residual rotation or vertical migration",
                "question_zh": "骨盆环与健侧对称——无残余旋转或垂直移位",
                "anchor5": "Symmetric on inlet and outlet views.",
                "why": "Vertical and rotational malreduction drives leg-length "
                       "discrepancy and sitting imbalance. Residual rotation "
                       "reaches 13.4 degrees here, and it is a whole-pelvis "
                       "judgement no per-piece transform makes.",
                "quant": "Complements rotation_deg (median 2.7, max 13.4).",
            },
            {
                "id": "P5",
                "scale": SCALE_A,
                "dimension_en": "Every piece",
                "dimension_zh": "各骨块",
                "question_en": "Every displaced piece has been reduced - none left where "
                               "it was, none moved to the wrong place",
                "question_zh": "每一移位骨块均已复位——既无遗留于移位状态者，也无被复位到错误位置者",
                "anchor5": "The whole pelvis is assembled, with every piece where it "
                           "belongs.",
                "why": "Cases here carry one to four pieces. The analysis scores "
                       "each piece against its own recorded transform, one at a "
                       "time, and never asks whether the assembled pelvis is "
                       "right.",
                "quant": "pieces_annotated (1 to 4 per case).",
            },
            {
                "id": "P6",
                "scale": SCALE_A,
                "dimension_en": "Fixation corridors",
                "dimension_zh": "固定通道",
                "question_en": "The reduced position leaves usable corridors for the "
                               "fixation I would plan",
                "question_zh": "复位后的位置为我会采用的固定方式留出了可用的通道",
                "anchor5": "An iliosacral screw, an anterior column screw or a plate "
                           "could be placed in this position.",
                "why": "A ring reduction exists to be held, usually by an "
                       "iliosacral screw whose corridor is a few millimetres "
                       "wide. A position that closes that corridor is undone at "
                       "the next step, and no metric looks for a corridor.",
                "quant": "Not measured anywhere.",
            },
            {
                "id": "P7",
                "scale": SCALE_A,
                "dimension_en": "Achievable",
                "dimension_zh": "可实现",
                "question_en": "This reduction is physically achievable - no pieces "
                               "sitting inside each other",
                "question_zh": "该复位在物理上可以实现——骨块之间无相互嵌插",
                "anchor5": "You could reach this position with standard manoeuvres "
                           "and clamps.",
                "why": "Each piece is moved by its own transform, so two pieces "
                       "can be placed into the same space while both transform "
                       "errors stay small and the plan is nonsense.",
                "quant": "Not measured; per-piece errors are independent.",
            },
        ],
    },
    {
        "task_id": "T6",
        "sheet": "T6_LongBone",
        "extension": "LongBoneFractureReduction",
        "title_en": "Long bone fracture reduction planning",
        "title_zh": "长骨骨折复位规划",
        "unit": "One fractured bone.",
        "materials": "3D of the reduced bone AP and lateral; axial pair at "
                     "proximal and distal reference levels for rotation; close "
                     "view of the fracture surfaces.",
        "comparator": "Partly - 7 of the 64 runs carry a surgeon's annotated "
                      "reduction; the rest are simulated displacements with a "
                      "known ground truth.",
        "runs_available": 64,
        "sample_n": 20,
        "quant": "Residual rotation and translation, point error, and the "
                 "clinical split where the shaft axis was recorded.",
        "gap": "No threshold in the workbook is bone-specific: 10 degrees of "
               "rotation is trivial in a humerus and a reoperation in a femur.",
        "items": [
            {
                "id": "L1",
                "scale": SCALE_A,
                "dimension_en": "Rotation",
                "dimension_zh": "旋转",
                "question_en": "Rotational alignment is correct for this bone",
                "question_zh": "该骨的旋转对线正确",
                "anchor5": "No malrotation you would correct.",
                "why": "The classic missed error of long bone surgery. Residual "
                       "malrotation is 0.0-4.7 degrees over these runs, which is "
                       "where clinical judgement and not a threshold decides - "
                       "the acceptable limit differs between a humerus and a "
                       "femur, and half this cohort is each.",
                "quant": "axial_rotation_deg (median 1.2, max 4.7).",
            },
            {
                "id": "L2",
                "scale": SCALE_A,
                "dimension_en": "Axial alignment",
                "dimension_zh": "轴向对线",
                "question_en": "Alignment is straight in both planes - no varus/valgus, "
                               "no angulation",
                "question_zh": "两个平面对线笔直——无内/外翻，无成角",
                "anchor5": "Straight in both planes on the reconstructed views.",
                "why": "What a postoperative radiograph shows and what drives "
                       "malunion; a plane-by-plane reading, not one residual "
                       "angle.",
                "quant": "angulation_deg (median 1.2, max 4.6).",
            },
            {
                "id": "L3",
                "scale": SCALE_A,
                "dimension_en": "Length",
                "dimension_zh": "长度",
                "question_en": "Length is restored - no shortening and no "
                               "over-distraction",
                "question_zh": "长度已恢复——无短缩，也无过度牵开",
                "anchor5": "Length matches the contralateral bone.",
                "why": "Well controlled in these runs (under 2 mm throughout), "
                       "which is exactly why it is worth one row: a length error "
                       "that appears in a new case would otherwise be reported "
                       "only inside a pooled residual.",
                "quant": "axial_error_mm (median 0.7, max 1.9).",
            },
            {
                "id": "L4",
                "scale": SCALE_A,
                "dimension_en": "Translation",
                "dimension_zh": "侧方移位",
                "question_en": "Side-to-side and front-to-back translation at the "
                               "fracture is acceptable",
                "question_zh": "骨折端的内外侧与前后方向移位在可接受范围内",
                "anchor5": "The shafts line up; no translation you would push "
                           "further.",
                "why": "The dominant residual error in this cohort by some way: "
                       "up to 9.85 mm of transverse offset, against under 5 "
                       "degrees of rotation and under 2 mm of length error. One "
                       "pooled residual reports all three as a single number and "
                       "hides which one moved.",
                "quant": "transverse_error_mm (median 2.0, max 9.9).",
            },
            {
                "id": "L5",
                "scale": SCALE_A,
                "dimension_en": "Bone contact",
                "dimension_zh": "骨面对合",
                "question_en": "The fracture surfaces meet well and do not overlap into "
                               "each other",
                "question_zh": "骨折面对合良好，无相互重叠嵌插",
                "anchor5": "Cortices meet all round with no bone inside bone.",
                "why": "A small rigid-body residual can still be an impossible "
                       "position if the fragments interpenetrate; contact is "
                       "what unites.",
                "quant": "truth_fit_mm (0.3-2.5 mm: the fracture closes, but not "
                         "how well it keys).",
            },
            {
                "id": "L6",
                "scale": SCALE_A,
                "dimension_en": "Complete reduction",
                "dimension_zh": "复位完整性",
                "question_en": "The reduction is complete - the fragment is not left "
                               "part-way between where it was and where it belongs",
                "question_zh": "复位完整——骨块未停留在移位位置与正确位置之间",
                "anchor5": "The displacement is taken out, not merely reduced.",
                "why": "These fragments start 10-67 degrees and 5-101 mm "
                       "displaced. Most runs remove 94% of that, but the worst "
                       "leaves 37% behind - a partial reduction that still "
                       "produces a small-looking residual next to a large "
                       "initial displacement.",
                "quant": "residual_fraction (median 0.06, max 0.37).",
            },
            {
                "id": "L7",
                "scale": SCALE_A,
                "dimension_en": "Fixation feasibility",
                "dimension_zh": "内固定可行性",
                "question_en": "The reduced position would allow the implant I would use "
                               "- nail or plate - to be applied",
                "question_zh": "复位后的位置可容纳我会使用的内固定物（髓内钉或钢板）",
                "anchor5": "The canal lines up for a nail, or a plate would sit on "
                           "bone along its length.",
                "why": "A reduction that cannot be held is not a reduction, and "
                       "a canal 2 mm off blocks a nail while barely moving any "
                       "surface metric.",
                "quant": "Not measured anywhere.",
            },
        ],
    },
    {
        "task_id": "T7",
        "sheet": "T7_Pedicle",
        "extension": "PedicleScrewPlanner",
        "title_en": "Pedicle screw planning",
        "title_zh": "椎弓根螺钉规划",
        "unit": "One patient's construct (worst screw - name its level and "
                "side).",
        "materials": "Axial at each pedicle isthmus, sagittal along each screw, "
                     "3D posterior view of the construct - the standard "
                     "Gertzbein-Robbins reading set.",
        "comparator": "No human plan is stored. Pairwise only if a surgeon plans "
                      "the same levels for the study.",
        "runs_available": 55,
        "sample_n": 20,
        "quant": "Gertzbein-Robbins grade, breach mm and direction, clearances, "
                 "containment, fill ratio, path HU.",
        "gap": "The grade is computed against a whole-vertebra label, so it "
               "cannot see the facet joint, the disc above, or whether the entry "
               "is reachable in a real posterior exposure.",
        "items": [
            {
                "id": "S1",
                "scale": SCALE_A,
                "dimension_en": "Containment",
                "dimension_zh": "骨内包容",
                "question_en": "The screw stays in the pedicle; any breach is lateral "
                               "and tolerable, never medial",
                "question_zh": "螺钉位于椎弓根内；如有穿破仅为外侧且可耐受，绝无内侧穿破",
                "anchor5": "Fully contained, cortex visible on all four walls.",
                "why": "Direction decides consequence. 23 of the 134 planned "
                       "screws breach medially and one crosses the medial wall "
                       "by 0.84 mm - the wall the roots sit behind - while the "
                       "grade counts only millimetres.",
                "quant": "grade / breach_direction (107 A, 27 B; 23 medial).",
            },
            {
                "id": "S2",
                "scale": SCALE_A,
                "dimension_en": "Facet preservation",
                "dimension_zh": "关节突保护",
                "question_en": "The entry point does not violate the facet joint of the "
                               "level above",
                "question_zh": "进钉点未侵犯上位节段的关节突关节",
                "anchor5": "The entry is lateral to and clear of the superior facet.",
                "why": "Facet violation at the top level drives adjacent segment "
                       "disease, and the analysis states outright that it cannot "
                       "compute it from a whole-vertebra label.",
                "quant": "Explicitly not computed (guide section 2.10).",
            },
            {
                "id": "S3",
                "scale": SCALE_A,
                "dimension_en": "Screw diameter",
                "dimension_zh": "螺钉直径",
                "question_en": "The screw diameter uses the pedicle properly - thick "
                               "enough for fixation, not so thick that it would burst "
                               "the wall",
                "question_zh": "螺钉直径与椎弓根相称——足以提供固定，又不致胀裂椎弓根壁",
                "anchor5": "The diameter you would have selected yourself for that "
                           "isthmus.",
                "why": "These runs are systematically thin: the median screw "
                       "fills 51% of the pedicle width against the 70-80% "
                       "usually aimed for, and only one screw in the cohort "
                       "reaches 92%. Under-filling costs pull-out strength and "
                       "reads as a safe plan.",
                "quant": "fill_ratio_pct (median 51%, p75 55%, target 70-80%).",
            },
            {
                "id": "S4",
                "scale": SCALE_A,
                "dimension_en": "Depth and length",
                "dimension_zh": "深度与长度",
                "question_en": "The screw reaches good depth in the body without "
                               "breaking the anterior cortex",
                "question_zh": "螺钉在椎体内达到良好深度，且未穿破椎体前缘皮质",
                "anchor5": "50-80% of body depth in good bone, anterior cortex "
                           "intact.",
                "why": "The two failure modes point in opposite directions - "
                       "pull-out against vascular injury - so the acceptable "
                       "window is a judgement, not a maximum. These runs sit at "
                       "59-85% of the available depth.",
                "quant": "length_of_depth_pct (median 75%); tip_to_cortex_mm (8-20 "
                         "mm).",
            },
            {
                "id": "S5",
                "scale": SCALE_A,
                "dimension_en": "Entry and trajectory",
                "dimension_zh": "进钉点与轨迹",
                "question_en": "The entry point and angles match a technique I would "
                               "use, and are reachable",
                "question_zh": "进钉点与角度符合我会采用的技术，且经计划入路可到达",
                "anchor5": "Straight-forward or anatomic trajectory, entry on a "
                           "landmark you can find intra-operatively.",
                "why": "A trajectory contained in bone can still need an entry "
                       "the exposure does not reach.",
                "quant": "Complements tpa_deg / spa_deg.",
            },
            {
                "id": "S6",
                "scale": SCALE_A,
                "dimension_en": "Bone quality",
                "dimension_zh": "骨质量",
                "question_en": "The bone along the screw path is of a quality that will "
                               "hold the screw",
                "question_zh": "螺钉路径沿途的骨质量足以把持螺钉",
                "anchor5": "Dense trabecular bone along the path, with cortical "
                           "purchase at the isthmus.",
                "why": "Path density spans 46-280 HU across these screws with no "
                       "threshold attached to it; whether that is enough depends "
                       "on the patient and on what the construct has to carry.",
                "quant": "path_hu (median 132, range 46-280).",
            },
            {
                "id": "S7",
                "scale": SCALE_A,
                "dimension_en": "Level and side labelling",
                "dimension_zh": "节段与侧别标注",
                "question_en": "Each screw is at the level it is labelled with, and on "
                               "the side it is labelled with",
                "question_zh": "每枚螺钉位于其标注的节段与标注的侧别",
                "anchor5": "Every label matches the anatomy you can see.",
                "why": "10 of the 134 screws carry a level label that disagrees "
                       "with the vertebra they are in, and the extension names "
                       "sides from a list index rather than from a coordinate - "
                       "on both reference runs every screw named _L is on the "
                       "patient's RIGHT. A mislabelled screw is a wrong-level or "
                       "wrong-side screw in theatre.",
                "quant": "name_agrees (10 of 134 disagree); side is recomputed, "
                         "never read.",
            },
            {
                "id": "S8",
                "scale": SCALE_A,
                "dimension_en": "Rod seating",
                "dimension_zh": "连接棒安装",
                "question_en": "The screw heads line up well enough for a rod to be "
                               "seated without excessive contouring",
                "question_zh": "各螺钉尾端排列良好，无需过度预弯即可安装连接棒",
                "anchor5": "The heads form a smooth line; a normally contoured rod "
                           "would drop in.",
                "why": "A construct is screws plus a rod. Individually perfect "
                       "screws whose heads do not line up force reduction onto "
                       "the rod, which loosens them - and every metric here is "
                       "computed one screw at a time.",
                "quant": "Not measured anywhere.",
            },
        ],
    },
    {
        "task_id": "T8",
        "sheet": "T8_Mandible",
        "extension": "BoneReconstructionPlanner",
        "title_en": "Mandible reconstruction with a fibula free flap",
        "title_zh": "腓骨游离皮瓣下颌骨重建",
        "unit": "One reconstruction (worst segment).",
        "materials": "3D of the neomandible from front, lateral and below; the "
                     "occlusion; the fibula segments with the pedicle side "
                     "marked; the donor fibula with the cut levels.",
        "comparator": "Only if the clinical plan used for the real operation is "
                      "available; the healthy-segment ground truth is predicted, "
                      "not a plan.",
        "runs_available": 2,
        "sample_n": 2,
        "quant": "Rv volume ratio, Ec contour error, Ep max projection, Dice, "
                 "HD95, per-segment protrusion.",
        "gap": "Every metric is against a predicted healthy segment, so it "
               "scores bone shape only. Occlusion, condylar seating, pedicle "
               "geometry and donor limits are outside it entirely.",
        "items": [
            {
                "id": "M1",
                "scale": SCALE_A,
                "dimension_en": "Resection margin",
                "dimension_zh": "切除安全缘",
                "question_en": "The mandibular osteotomies leave an adequate margin from "
                               "the lesion",
                "question_zh": "下颌骨截骨线与病灶之间保留了足够的安全缘",
                "anchor5": "The margin you would accept for this pathology, at both "
                           "cut ends.",
                "why": "The one oncological decision in the plan. Every metric "
                       "is computed against a healthy segment PREDICTED from the "
                       "resected mandible, which assumes the cuts were already "
                       "right.",
                "quant": "Not measured anywhere.",
            },
            {
                "id": "M2",
                "scale": SCALE_A,
                "dimension_en": "Contour and symmetry",
                "dimension_zh": "轮廓与对称",
                "question_en": "The reconstructed mandible restores contour and "
                               "lower-face symmetry",
                "question_zh": "重建后的下颌恢复了下颌轮廓与下面部对称性",
                "anchor5": "Symmetric chin projection and gonial angle; a "
                           "cosmetically acceptable lower face.",
                "why": "The visible result of the operation. Contour error is "
                       "4.3 mm on both saved runs, but it is averaged over only "
                       "the half of the contour a fibula can reach, so it cannot "
                       "be read as a verdict on the face.",
                "quant": "contour_error_mm 4.3 at contour_coverage 48-52%.",
            },
            {
                "id": "M3",
                "scale": SCALE_A,
                "dimension_en": "Occlusion and condyle",
                "dimension_zh": "咬合与髁突",
                "question_en": "The condyles stay seated and the occlusion is preserved",
                "question_zh": "髁突保持就位，咬合关系得以保持",
                "anchor5": "Condyles concentric, occlusion reproducible without "
                           "repositioning.",
                "why": "A neomandible with the right shape and a distracted "
                       "condyle is a failed reconstruction; nothing in the "
                       "metrics looks at the joint.",
                "quant": "Not measured anywhere.",
            },
            {
                "id": "M4",
                "scale": SCALE_A,
                "dimension_en": "Segment lengths",
                "dimension_zh": "骨段长度",
                "question_en": "The number of fibula segments is the smallest that gives "
                               "this contour, and no segment is too short to survive",
                "question_zh": "腓骨骨段数量是达成该轮廓所需的最少段数，且无过短而难以存活的骨段",
                "anchor5": "Every osteotomy earns its place; no segment under about "
                           "2 cm.",
                "why": "Both saved runs use three segments, and one of them is "
                       "11.3 mm long - under half the length usually accepted as "
                       "viable. Each extra osteotomy is another junction that "
                       "can fail to unite, a cost the contour metrics reward you "
                       "for ignoring.",
                "quant": "segment_lengths_mm (11.3, 20.4, 21.4 on one run).",
            },
            {
                "id": "M5",
                "scale": SCALE_A,
                "dimension_en": "Junction contact",
                "dimension_zh": "接合面对合",
                "question_en": "The bone ends meet well at every junction",
                "question_zh": "各接合处骨端对合良好",
                "anchor5": "Broad flush contact at every junction, native bone "
                           "included.",
                "why": "Non-union at a junction is the commonest reoperation, "
                       "and contact is measured nowhere - the metrics compare "
                       "the graft with a predicted shape, not the graft with "
                       "itself.",
                "quant": "Not measured anywhere.",
            },
            {
                "id": "M6",
                "scale": SCALE_A,
                "dimension_en": "Position in the jaw line",
                "dimension_zh": "在下颌轮廓中的位置",
                "question_en": "The graft sits at the right height and no segment "
                               "protrudes outside the mandibular outline",
                "question_zh": "移植骨高度合适，且无骨段突出于下颌轮廓之外",
                "anchor5": "Flush with the jaw line, and at a height that would "
                           "still allow dental implants later.",
                "why": "The fibula sits 2.5-2.8 mm inside the mandibular outline "
                       "on these runs while a segment protrudes 7.1 mm on one "
                       "and 12.2 mm on the other. A protruding segment is "
                       "palpable and can perforate mucosa; too low a graft "
                       "forecloses implants.",
                "quant": "max_projection_mm (7.1 and 12.2); median_offset_mm "
                         "(-2.8, -2.5).",
            },
            {
                "id": "M7",
                "scale": SCALE_A,
                "dimension_en": "Flap feasibility",
                "dimension_zh": "皮瓣可行性",
                "question_en": "The segment layout works with the fibula pedicle and "
                               "stays within donor limits",
                "question_zh": "各骨段的摆放与腓血管蒂相容，且在供区可取范围内",
                "anchor5": "Pedicle runs continuously to the recipient vessels; "
                           "proximal and distal safe zones preserved.",
                "why": "The constraint that makes a mandibular plan buildable, "
                       "and it lives in the leg, which the metrics never look "
                       "at. One run needs 135 mm of fibula, the other 45 mm.",
                "quant": "total_graft_length_mm; donor limits not checked.",
            },
            {
                "id": "M8",
                "scale": SCALE_A,
                "dimension_en": "Plate seating",
                "dimension_zh": "钛板就位",
                "question_en": "A reconstruction plate can be seated along the "
                               "neomandible and fixed to native bone at both ends",
                "question_zh": "重建钛板可沿重建后的下颌就位，并在两端固定于自体骨",
                "anchor5": "A continuous plate path with enough native bone at each "
                           "end for screws.",
                "why": "The fixation that holds the whole reconstruction "
                       "together, and a segment layout can be geometrically "
                       "ideal and leave nowhere to run a plate.",
                "quant": "Not measured anywhere.",
            },
        ],
    },
]

#: Where a blinded pairwise comparison is possible today, which is not the same
#: as "a ground truth exists": a ground truth is anatomy, a comparator is
#: somebody's plan.
PAIRWISE_TASKS = ("T1", "T3", "T5", "T6")

#: Minutes per case. Not a constant: a pelvis with six fragments and a construct
#: of eight screws take longer to read than one orbit, and the panel's time
#: budget is what decides the sample size.
MINUTES_PER_CASE = {
    "T1": 3, "T2": 3, "T3": 3, "T4": 3, "T5": 4, "T6": 3, "T7": 4, "T8": 4,
}

#: The table the analysis consumes: one row per (rater, case, question). Long
#: rather than wide because every analysis takes it in this shape, and a wide
#: sheet has to be melted before anything can start.
RESPONSE_COLUMNS = [
    ("rater_id", "Opaque rater code, R01..."),
    ("task_id", "T1...T8"),
    ("case_id", "Opaque case code from the randomisation key"),
    ("arm", "Blank until unblinding: pipeline / manual / duplicate"),
    ("item_id", "A task question (Z1, O1, ...), G1 or G2"),
    ("score", "1-5, the pairwise -2..+2, or NA"),
    ("comment", "Free text; the worst element is named here"),
    ("submitted_utc", "When the case was submitted"),
]


def items_for(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    """The task's own detailed questions first, then the two closing ones.

    Order is the instrument, not presentation. A rater who is asked "would you
    use this plan" before looking at anything answers on impression; asked after
    six to eight specific questions, the same person answers on what they have
    just found. The closing pair is identical on all eight forms, which is what
    lets them pool into one cross-procedure figure.
    """
    items = list(task["items"]) + list(CORE_ITEMS)
    if task["task_id"] in PAIRWISE_TASKS:
        items.append(dict(PAIRWISE_ITEM))
    return items


#: Questions defined above but withheld from the deployed collection sheets. Empty
#: on purpose: a procedure carries as many questions as it needs (6 to 8), and the
#: count is not levelled across the eight. Naming an id here drops that question
#: from every sheet AND makes the reference document say so and say what it cost,
#: which is the only safe way to shorten a form -- G2 is the sole question asking
#: whether a plan can physically be carried out, and PW the sole comparison
#: against current practice.
NOT_COLLECTED: Tuple[str, ...] = ("PW",)


def case_form_items(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    """What one per-procedure collection sheet actually asks: safety, overall
    acceptability, then the task's own questions."""
    return [item for item in items_for(task)
            if item["id"] not in NOT_COLLECTED]


def sample_size(task: Dict[str, Any]) -> int:
    return min(task["sample_n"], task["runs_available"])


def duplicates(task: Dict[str, Any]) -> int:
    """10% of a task's cases are shown twice, for intra-rater reliability."""
    return max(1, int(math.ceil(sample_size(task) * 0.1)))


def collects_pairwise(task: Dict[str, Any]) -> bool:
    """A human plan exists AND the pairwise question is actually being asked.
    The two are different facts, and the budget depends on the second."""
    return task["task_id"] in PAIRWISE_TASKS and "PW" not in NOT_COLLECTED


def minutes_per_rater(task: Dict[str, Any]) -> int:
    """A pairwise case shows two plans, so it costs about half as much again."""
    cases = sample_size(task) + duplicates(task)
    factor = 1.5 if collects_pairwise(task) else 1.0
    return int(round(cases * MINUTES_PER_CASE[task["task_id"]] * factor))


# ---------------------------------------------------------------------------
# The rater's workbook: eight sheets, nothing else
# ---------------------------------------------------------------------------

Block = Tuple[str, Sequence[str], Sequence[Dict[str, Any]]]
Sheet = Tuple[str, Sequence[Block]]


def _task_sheet(task: Dict[str, Any]) -> Sheet:
    """One self-contained form. A rater may be sent a single tab, so everything
    needed to fill it in is on it, and nothing else is.

    Asks ``case_form_items``, not ``items_for``: two rater-facing artefacts that
    ask different questions is the drift this module exists to prevent, so this
    workbook carries whatever the per-procedure collection sheets carry."""
    items = case_form_items(task)

    header_rows = [{"Field / 项目": "%s / %s" % (en, zh), "Fill in / 填写": ""}
                   for en, zh in HEADER_FIELDS]

    how_rows = [{"English": en, "中文": zh} for en, zh in FORM_INSTRUCTIONS]

    form_rows = []
    for number, item in enumerate(items, start=1):
        form_rows.append({
            "No.": number,
            "Question (English)": item["question_en"],
            "问题（中文）": item["question_zh"],
            "Score / 评分": "",
            "Comment / 备注": "",
        })

    free_rows = [{"Question (English)": en, "问题（中文）": zh,
                  "Answer / 作答": ""} for en, zh in FREE_TEXT]

    blocks = [
        ("%s  %s / %s" % (task["task_id"], task["title_en"], task["title_zh"]),
         ["Field / 项目", "Fill in / 填写"], header_rows),
        ("How to score / 评分方法", ["English", "中文"], how_rows),
        ("Please score every row / 请为每一行评分", FORM_COLUMNS, form_rows),
        ("Comments / 意见", ["Question (English)", "问题（中文）", "Answer / 作答"],
         free_rows),
    ]
    return task["sheet"], blocks


def build_sheets() -> List[Sheet]:
    """The rater-facing workbook: one tab per procedure and no supporting tabs.

    Everything a rater does not need to fill the form in -- the rationale, the
    protocol, the analysis plan -- is in the developer document instead. A form
    carrying its own justification is a form people read instead of filling in.
    """
    return [_task_sheet(task) for task in TASKS]


# ---------------------------------------------------------------------------
# The developer's document
# ---------------------------------------------------------------------------

DOC_TEMPLATE = """# Qualitative evaluation of the planning results

The per-procedure analyses in `SlicerAIAgentLib/experiments/` measure how far a
plan is from the ground truth in millimetres. They cannot say whether a surgeon
would use it, and on this data nothing on disk can: the same millimetre is
trivial in one direction and a reoperation in another. This document is the
overview of the panel study that answers that question, and of the instrument
this folder holds:

| file | what it is |
|---|---|
| `<Procedure>.xlsx` (8 of them) | **what the panel fills in** - questions down the rows, cases across the columns |
| `Likert_rating_forms.xlsx` | the same questions one case per tab, with comment and free-text fields |
| this document | design, protocol, analysis plan, and the rationale behind every question |

Regenerate from one source:

```bash
python scripts/build_likert_case_forms.py  # the per-procedure collection sheets
python scripts/build_likert_forms.py       # the reference workbook and this document
```

Neither script overwrites an existing collection sheet without `--force`, so a
hand-edited form stays hand-edited.

The instrument is defined in `SlicerAIAgentLib/experiments/likert.py`. The
workbook is rater-facing and bilingual; this document is developer-facing and
English, and the two cannot drift apart because both are rendered from that
module.

---

## 1. The instrument

Every procedure gets **six to eight detailed questions of its own**, and then
the same **two closing questions**. That is {count_range} in all, and the count
is deliberately not levelled across the eight: a form asks what its operation
needs and stops.

The detailed questions come first. A rater asked "would you use this plan"
before looking at anything answers on impression; the same person asked after
eight specific questions answers on what they have just found - and the specific
answers are what tell you *why* a plan was rejected.

The two closing questions are identical everywhere, which is what lets the eight
forms pool into one cross-procedure figure:

| # | Dimension | Question | Scale |
|---|---|---|---|
{core_table}

A detailed question earned its place only if **a surgeon would refuse or revise
the plan because of it** and **the existing metrics cannot already see it**.
Section 6 lists all of them with both answers. Note that "could this be carried
out" is asked concretely, per procedure - drillable through a standard intraoral
approach, insertable through a transconjunctival incision, a rod that seats
without contouring - rather than once in the abstract, because the abstract form
of that question is answerable without looking at the plan.

{task_table}

Three scales, and most rows use the first:

- **Agreement, 1-5** - every statement question. 5 = strongly agree.
- **Acceptability, 1-5** - question G2 only, the primary endpoint. Phrased as a
  decision (use as planned -> discard) rather than as agreement, so that
  "score >= 4" means "a surgeon would use it without re-planning" instead of
  whatever each rater privately took "acceptable" to mean.
- **Pairwise, -2..+2** - question PW, on the four procedures where a plan the
  surgeon drew for the same patient is on disk. It is the only question that
  needs *two* plans rendered as A and B, so it decides what the materials
  pipeline has to produce.

Both non-default scales print their levels inside the question text, so the form
needs no legend.
{omissions_block}
Two rules carry more weight than the wording:

- **Worst-element scoring.** A plan is delivered whole, so a question covering
  several implants, screws or fragments is scored on the *worst* one and the
  rater names it. Averaging elements hides the one screw that makes the construct
  unusable.
- **The safety veto.** G1 <= 2 from any single rater marks the case unsafe
  whatever the other questions say, and is reported case by case, never inside a
  mean.

---

## 2. Experimental design

**Panel.** 3 raters per procedure (5 where the procedure carries the paper's
headline claim), consultant level, at least two centres, none involved in
building the system. One rater per procedure who does not routinely use planning
software, so "acceptable" is not read through the habits of one tool.

**Sampling.** Not all {total_runs} runs. Per procedure, a stratified random
sample drawn by **tertiles of that procedure's headline metric**, plus every case
the quantitative analysis flagged as an outlier. A sample of good cases cannot
calibrate a threshold. Oversampled strata are labelled in the key so proportions
can be re-weighted.

**Materials.** Generated by script from each run's own
`Statistic/scene/scene.mrml`, so the view set is identical for every case and
every arm: same cameras, same window level, same colours. Two things must happen
there or blinding fails - **strip node names** (`OFR_Reconstructed_Seg` announces
the arm) and put both arms through the identical pipeline. Ship the fixed PNG set
plus the `.mrb`, so a rater who wants to rotate the scene can.

**Blinding.** Opaque case IDs, order randomised per rater, arms randomised to A/B
per case, key held by a non-rater until the last submission.

**Calibration.** One 30-minute session before rating: the panel scores the same
three practice cases and argues about what a 3 means. Practice cases are excluded.
Without it, each rater's first ten cases measure the instrument rather than the
plans.

**Ethics.** Retrospective de-identified imaging, no change to any patient's care -
normally a waiver - but it is a study with human raters, so obtain the waiver and
record rater consent before the first rating, not at submission.

**Budget.**

| Task | Cases | + duplicates | Pairwise | Minutes per rater | Rater-hours (n=3) |
|---|---|---|---|---|---|
{budget_table}

Minutes are one rater on that procedure; a rater normally covers one procedure,
not all eight.

---

## 3. Data collection

The unit is one (rater, case, question). Collect in long format:

| Column | Meaning |
|---|---|
{response_table}

A web form or REDCap is preferable to the spreadsheet only because it makes
timestamps, one-case-at-a-time presentation and the "NA needs a reason" rule
automatic. The workbook is the fallback and the published supplement.

Keep three things beside the ratings, or the analysis cannot be reconstructed:
the randomisation key, the sampling key (which case came from which stratum), and
the exact material each rater saw.

---

## 4. Data analysis

Treat the scores as **ordinal**. Averaging Likert scores assumes the step from 2
to 3 is the step from 4 to 5, and here it is not.

1. **Primary endpoint.** Share of cases with G2 >= 4, per task and pooled, with
   Wilson 95% CI. Consensus per case = median of the raters; report the per-rater
   shares beside it. (20 cases at 90% gives roughly 70-97%; pooling the eight
   procedures narrows it to about +/-5%.)
2. **Per question.** Median and IQR, and the share >= 4. Report floor and ceiling
   effects: a question everyone scores 5 on every case measures nothing and
   should be dropped from the next round.
3. **Safety.** Every case with G1 <= 2 from any rater, listed individually with
   the comment. Never inside a mean.
4. **Agreement between raters.** Gwet AC2 with ordinal weights as the primary
   statistic, because kappa and Krippendorff alpha collapse toward zero when
   nearly every case is rated 4-5, which is the distribution to expect. Report
   alpha, percent agreement within one point, and ICC(2,k) beside it, and
   pre-register all four so the choice is not made after seeing them.
5. **Agreement within a rater.** Weighted kappa on the 10% duplicated cases.
6. **Against current practice.** T1/T3/T5/T6, from question PW: Wilcoxon
   signed-rank on the pairwise score against 0, and the share where the system is
   at least as good, with a pre-specified non-inferiority margin.
7. **Do the metrics predict the surgeon?** The result that pays for the whole
   exercise: Spearman rho between each task's headline metric and G2, then an ROC
   of that metric against "acceptable" (G2 >= 4). The Youden point is a
   clinically calibrated threshold - the first time HD95, breach_mm or delta has
   one on this data.
8. **Free text.** Two coders build a failure-mode taxonomy from the first 20% of
   comments, code the rest independently, report kappa on the codes and the
   frequency of each failure mode per procedure. This is the part that tells you
   what to fix; the numbers only tell you that something is wrong.

Report the reliability half against GRRAS: rater number, specialty, years,
centres, independence from the developers, the calibration session, the scale,
the blinding, and the pre-registered analysis. Publish the instrument as a
supplement.

---

## 5. Two honest limitations

- **T8 (mandible) has 2 runs on disk.** Its panel result will be anecdotal until
  more cases are run; say so rather than reporting a percentage of two.
- **T2, T4 and T7 carry no pairwise question.** They have reference *anatomy* - a
  labelled correct orbit, a removed bone flap, vertebra labels - which is not a
  competing plan, and comparing against it would be scoring the system against
  its own ground truth. Their result is an absolute acceptability rate, and the
  question is omitted rather than faked.

---

## 6. Question reference

What a 5 means, why the question is on the form, and which metric it sits beside.
None of this reaches the rater.

{reference_table}
"""


def _markdown_escape(text: str) -> str:
    return str(text).replace("|", "\\|")


def _row(cells: Sequence[Any]) -> str:
    return "| " + " | ".join(_markdown_escape(cell) for cell in cells) + " |"


def build_markdown() -> str:
    """Render the developer document from the same data as the workbook."""
    core_table = "\n".join(
        _row([item["id"], item["dimension_en"], item["question_en"],
              item["scale"]])
        for item in CORE_ITEMS if item["id"] not in NOT_COLLECTED)

    task_lines = ["| Task | Procedure | n | Its own questions | "
                  "Human plan on disk | Runs on disk |",
                  "|---|---|---|---|---|---|"]
    for task in TASKS:
        specific = ", ".join("%s %s" % (item["id"], item["dimension_en"])
                             for item in task["items"])
        task_lines.append(_row([
            task["task_id"],
            "%s / %s" % (task["title_en"], task["title_zh"]),
            len(case_form_items(task)),
            specific,
            "yes" if task["task_id"] in PAIRWISE_TASKS else "no",
            task["runs_available"]]))
    task_table = "\n".join(task_lines)

    budget_table = "\n".join(
        _row([task["task_id"], sample_size(task), duplicates(task),
              "yes" if collects_pairwise(task) else "no",
              minutes_per_rater(task),
              round(minutes_per_rater(task) * 3 / 60.0, 1)])
        for task in TASKS)

    response_table = "\n".join(_row([("`%s`" % name), meaning])
                               for name, meaning in RESPONSE_COLUMNS)

    reference_lines = []
    for task in TASKS:
        reference_lines.append("")
        reference_lines.append("### %s %s / %s"
                               % (task["task_id"], task["title_en"],
                                  task["title_zh"]))
        reference_lines.append("")
        reference_lines.append("*Rating unit:* %s  " % task["unit"])
        reference_lines.append("*Shown to the rater:* %s  " % task["materials"])
        reference_lines.append("*Comparator:* %s  " % task["comparator"])
        reference_lines.append("*Metrics beside it:* %s  " % task["quant"])
        reference_lines.append("*What they cannot see:* %s" % task["gap"])
        reference_lines.append("")
        reference_lines.append("| # | A 5 means | Why this question | "
                               "Quantitative counterpart |")
        reference_lines.append("|---|---|---|---|")
        for item in items_for(task):
            label = item["id"]
            if label in NOT_COLLECTED:
                label += " *(not collected)*"
            reference_lines.append(_row([label, item["anchor5"],
                                         item["why"], item["quant"]]))
    reference_table = "\n".join(reference_lines).strip()

    counts = sorted(set(len(case_form_items(task)) for task in TASKS))
    count_range = ("%d" % counts[0] if len(counts) == 1
                   else "%d to %d" % (counts[0], counts[-1]))

    # Rendered only when something is actually withheld, so the document cannot
    # describe an omission that is not in force -- or hide one that is.
    omissions_block = ""
    withheld = [item for item in list(CORE_ITEMS) + [PAIRWISE_ITEM]
                if item["id"] in NOT_COLLECTED]
    if withheld:
        lines = ["", "**Withheld from the deployed forms** "
                     "(`likert.NOT_COLLECTED`); remove an id there and every "
                     "form carries the question again:", ""]
        for item in withheld:
            reason = item["why"][:1].lower() + item["why"][1:]
            lines.append("- **%s, %s** - %s" % (item["id"],
                                                item["dimension_en"].lower(),
                                                reason))
        lines.append("")
        omissions_block = "\n".join(lines)

    return DOC_TEMPLATE.format(
        core_table=core_table,
        task_table=task_table,
        count_range=count_range,
        omissions_block=omissions_block,
        budget_table=budget_table,
        response_table=response_table,
        reference_table=reference_table,
        total_runs=sum(task["runs_available"] for task in TASKS),
    )
