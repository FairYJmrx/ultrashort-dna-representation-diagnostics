| Task                 | Condition              |   Length | Representation        | Best readout     |   Macro-F1 |   Accuracy |   Features |
|:---------------------|:-----------------------|---------:|:----------------------|:-----------------|-----------:|-----------:|-----------:|
| Target/background    | 3% N mask              |       69 | CSP                   | nearest_centroid |      0.604 |      0.632 |        147 |
| Target/background    | 3% N mask              |       75 | Canonical 5-mer       | nearest_centroid |      0.692 |      0.730 |        508 |
| Target/background    | 3% N mask              |      100 | Canonical 5-mer       | logistic         |      0.698 |      0.718 |        511 |
| Target/background    | 3% N mask              |      150 | Canonical 5-mer       | nearest_centroid |      0.693 |      0.704 |        510 |
| Target/background    | Clean                  |       69 | CSP                   | nearest_centroid |      0.670 |      0.684 |        147 |
| Target/background    | Clean                  |       75 | Canonical 5-mer       | nearest_centroid |      0.653 |      0.703 |        508 |
| Target/background    | Clean                  |      100 | Canonical 5-mer       | nearest_centroid |      0.738 |      0.778 |        508 |
| Target/background    | Clean                  |      150 | Canonical 5-mer       | nearest_centroid |      0.703 |      0.704 |        510 |
| Target/background    | 1% substitution        |       69 | Canonical spaced seed | nearest_centroid |      0.749 |      0.763 |        136 |
| Target/background    | 1% substitution        |       75 | Canonical 7-mer       | mlp              |      0.621 |      0.649 |       4637 |
| Target/background    | 1% substitution        |      100 | Canonical 5-mer       | logistic         |      0.698 |      0.718 |        512 |
| Target/background    | 1% substitution        |      150 | Canonical 5-mer       | nearest_centroid |      0.775 |      0.778 |        512 |
| Target/background    | 1% substitution + 3% N |       69 | Canonical spaced seed | nearest_centroid |      0.730 |      0.737 |        136 |
| Target/background    | 1% substitution + 3% N |       75 | CSP                   | logistic         |      0.676 |      0.684 |        147 |
| Target/background    | 1% substitution + 3% N |      100 | CSP                   | nearest_centroid |      0.666 |      0.667 |        147 |
| Target/background    | 1% substitution + 3% N |      150 | CSP                   | mlp              |      0.649 |      0.667 |        147 |
| Target/background    | 5-bp trim              |       69 | Canonical spaced seed | nearest_centroid |      0.622 |      0.632 |        136 |
| Target/background    | 5-bp trim              |       75 | Canonical 5-mer       | nearest_centroid |      0.713 |      0.730 |        508 |
| Target/background    | 5-bp trim              |      100 | Canonical spaced seed | nearest_centroid |      0.688 |      0.722 |        136 |
| Target/background    | 5-bp trim              |      150 | Canonical 5-mer       | nearest_centroid |      0.703 |      0.704 |        510 |
| Within-genus species | 3% N mask              |       69 | Canonical 5-mer       | mlp              |      0.540 |      0.556 |        502 |
| Within-genus species | 3% N mask              |       75 | CSP                   | logistic         |      0.613 |      0.615 |        147 |
| Within-genus species | 3% N mask              |      100 | Canonical 7-mer       | mlp              |      0.652 |      0.652 |       3731 |
| Within-genus species | 3% N mask              |      150 | Canonical 5-mer       | nearest_centroid |      0.693 |      0.704 |        510 |
| Within-genus species | Clean                  |       69 | Canonical 7-mer       | mlp              |      0.550 |      0.556 |       3626 |
| Within-genus species | Clean                  |       75 | CSP                   | mlp              |      0.549 |      0.615 |        147 |
| Within-genus species | Clean                  |      100 | Canonical 7-mer       | logistic         |      0.673 |      0.696 |       4286 |
| Within-genus species | Clean                  |      150 | Canonical 5-mer       | nearest_centroid |      0.703 |      0.704 |        510 |
| Within-genus species | 1% substitution        |       69 | Canonical 5-mer + CSP | mlp              |      0.590 |      0.593 |        653 |
| Within-genus species | 1% substitution        |       75 | CSP                   | mlp              |      0.594 |      0.615 |        147 |
| Within-genus species | 1% substitution        |      100 | Canonical 5-mer       | nearest_centroid |      0.564 |      0.565 |        512 |
| Within-genus species | 1% substitution        |      150 | Canonical 5-mer       | nearest_centroid |      0.775 |      0.778 |        512 |
| Within-genus species | 1% substitution + 3% N |       69 | Canonical 7-mer       | mlp              |      0.571 |      0.593 |       3182 |
| Within-genus species | 1% substitution + 3% N |       75 | Canonical 5-mer       | logistic         |      0.561 |      0.577 |        508 |
| Within-genus species | 1% substitution + 3% N |      100 | Canonical 5-mer + CSP | nearest_centroid |      0.522 |      0.522 |        657 |
| Within-genus species | 1% substitution + 3% N |      150 | CSP                   | mlp              |      0.649 |      0.667 |        147 |
| Within-genus species | 5-bp trim              |       69 | Canonical 5-mer       | nearest_centroid |      0.593 |      0.593 |        502 |
| Within-genus species | 5-bp trim              |       75 | Canonical 7-mer       | logistic         |      0.578 |      0.654 |       3645 |
| Within-genus species | 5-bp trim              |      100 | Canonical 5-mer       | mlp              |      0.544 |      0.565 |        511 |
| Within-genus species | 5-bp trim              |      150 | Canonical 5-mer       | nearest_centroid |      0.703 |      0.704 |        510 |
