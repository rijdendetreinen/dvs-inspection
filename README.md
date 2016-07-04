# dvs-inspection

A very simple tool to inspect InfoPlus DVS messages for known problems, currently:

* Departure messages that arrive shorter than 70 minutes before real departure

## Input

A text file containing DVS messages, one per line

## Output

List of problematic services, statistics.

Example:

```
2016-07-02 12:38:00 29625 DV DV_29625_2016-07-02 2779.432
2016-07-02 15:03:00 2671 RTST RTST_2671_2016-07-02 1216.413
2016-07-02 15:07:00 2654 RTST RTST_2654_2016-07-02 779.52

Stats
=====
2016-06-30: Totaal 198804 berichten. 51305 ritten, 238 te laat = 0.46 procent
2016-07-02: Totaal 152628 berichten. 45105 ritten, 37 te laat = 0.08 procent
2016-07-01: Totaal 204943 berichten. 51662 ritten, 127 te laat = 0.25 procent
2016-06-29: Totaal 194917 berichten. 51394 ritten, 370 te laat = 0.72 procent
2016-06-28: Totaal 2259 berichten. 634 ritten, 1 te laat = 0.16 procent
```
