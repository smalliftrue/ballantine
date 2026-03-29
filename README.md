# ballantine
A shorthand-based stat tracker for basketball.

# REGULAR GAME ACTIONS:

[ACTION][PLAYER],[ANY APPENDAGES]

Players Team 1:
q w e r t

Players Team 2:
a s d f g

1 : Free Throw; valid appendages: 4 ONLY IF -

2 : 2p; valid appendages: 4 ONLY IF -, 5 ONLY IF +, 6 ONLY IF -

3 : 3p; valid appendages: 4 ONLY IF -, 5 ONLY IF +, 6 ONLY IF -

4 : rebound; CANNOT BE FIRST

5 : assist; CANNOT BE FIRST

6 : block; CANNOT BE FIRST

7 : foul; valid appendages: none

8 : turnover; valid appendages: 9

9 : steal; CANNOT BE FIRST


\- : shot miss

= : shot make

The prior modifiers only apply to 1, 2, and 3 (so 1=, 1-...)

IDENTs 4, 5, 6, and 9 may not occur as the FIRST action, and must appear after a comma.

Some examples:

3=q,5w : Q THREE, ASSIST W

2-w,6a,4s : W TWO MISS, BLOCKED A, DEF REB S

7a : 7 foul

# SUBSTITUTIONS:

;[SHORTCUT],[NUMBER]

;q,23 : SUBSTITUTION OF Q OFF, 23 COMES ON

# CHANGING QUARTERS:

] : QUARTER PLUS 1, INCLUDES OVERTIME

.: ENDS THE GAME, PRINTS STAT SHEETS
