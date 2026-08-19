## PelvicFracturePlanning

1. [op=user_choice] In the "Input CT Volume" option, choose the Pelvic Volume.
2. [op=extension_op] Click "Run Step 1: Segment Pelvis" button.
3. [op=extension_op] Click "Run Step 2: Segment Fractures" button.
4. [op=user_choice] In the "Untick a piece to stop treating it as separate" section, untick these segments.
5. [op=branch_op] If a piece should have been split but was and and require cut it manually, jump to step 6. If not, jump to step 9.
6. [op=extension_op] Click "Manually seperate" button.
7. [op=user_interaction] Manually click to add a cut point and adjust the position and rotation of the cutting plane.
8. [op=extension_op] Click "Confirm seperation" button.
9. [op=extension_op] Click "Run Step 3: Generate template" button.
10. [op=branch_op] If further adjustments of the template are required, tick the "Manually adjust a template" checkbox. If not, jump to step 15.
11. [op=user_choice] In the "Template" option, Choose which template needs adjustment in the "Template" selection box.
12. [op=user_interaction] Manually adjust the position and rotation of the selected template.
13. [op=branch_op] If more templates need adjustment, jump to step 11. If not, jump to step 14.
14. [op=extension_op] Click the "Apply template adjustment" button.
15. [op=extension_op] Click "Run Step 4: Register _Reduce" button.
16. [op=branch_op] If further adjustments are required, tick the "Manually adjust a fragment" checkbox. If not, jump to step 21.
17. [op=user_choice] In the "Fragment" option, Choose which fragment needs adjustment in the "Fragment" selection box.
18. [op=user_interaction] Manually adjust the position and rotation of the selected fragment.
19. [op=branch_op] If further adjustments are required, jump to step 17. If not, jump to step 20.
20. [op=extension_op] Click the "Apply adjustments" button.
21. [op=extension_op] Click the "Run Step 5: Plan Screws" button.
22. [op=branch_op] If further adjustments are required, tick the "Edit Screw trajectories" checkbox. If not, stop here.
23. [op=user_interaction] Manually adjust the position and rotation of the screw trajectories.
24. [op=extension_op] Click the "Regenerate screws from edited lines" button.