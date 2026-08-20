## PelvicFracturePlanning

1. [op=user_choice] In the "Input CT Volume" option, choose the Pelvic Volume.
2. [op=extension_op] Click "Run Step 1: Segment Pelvis" button.
3. [op=slicer_op] For the 3D view, click the "Center view" botton.
4. [op=extension_op] Click "Run Step 2: Segment Fractures" button.
5. [op=user_choice] In the "Untick a piece to stop treating it as separate" section, untick these segments.
6. [op=branch_op] If a piece should have been split but was and and require cut it manually, jump to step 7. If not, jump to step 10.
7. [op=extension_op] Click "Manually seperate" button.
8. [op=user_interaction] Manually click to add a cut point and adjust the position and rotation of the cutting plane.
9. [op=extension_op] Click "Confirm seperation" button.
10. [op=extension_op] Click "Run Step 3: Generate template" button.
11. [op=branch_op] If further adjustments of the template are required, tick the "Manually adjust a template" checkbox. If not, jump to step 13.
12. [op=user_choice] In the "Template" option, Choose which template needs adjustment in the "Template" selection box.
13. [op=extension_op] Click the "Apply template adjustment" button.
14. [op=extension_op] Click "Run Step 4: Register _Reduce" button.
15. [op=branch_op] If further adjustments are required, tick the "Manually adjust a fragment" checkbox. If not, jump to step 17.
16. [op=user_choice] In the "Fragment" option, Choose which fragment needs adjustment in the "Fragment" selection box.
17. [op=extension_op] Click the "Apply adjustments" button.
18. [op=extension_op] Click the "Run Step 5: Plan Screws" button.
19. [op=branch_op] If further adjustments are required, tick the "Edit Screw trajectories" checkbox. If not, stop here.
20. [op=user_choice] In the "Trajectory" option, Choose which trajectory needs adjustment in the "Trajectory" selection box.
21. [op=extension_op] Click the "Regenerate screws from edited lines" button.