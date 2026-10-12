# Data sources

All datasets are real, published data. The CSV files were downloaded from the
Rdatasets archive (Arel-Bundock, https://vincentarelbundock.github.io/Rdatasets/),
which redistributes datasets that ship with R packages. Nothing here was generated or
edited.

| File | R package::name | Original source |
|---|---|---|
| `movielens.csv.gz` | dslabs::movielens | MovieLens "latest-small", GroupLens Research, University of Minnesota. Harper & Konstan (2015), *ACM TiiS* 5(4):19. 100,004 ratings, 671 users, 9,066 movies. Gzipped; Spark reads it directly. |
| `UCBAdmissions.csv` | datasets::UCBAdmissions | Bickel, Hammel & O'Connell (1975), "Sex bias in graduate admissions: Data from Berkeley", *Science* 187:398–404. |
| `sleep.csv` | datasets::sleep | Cushny & Peebles (1905), *J. Physiology* 32:501–510; analysed by "Student" (1908), *Biometrika* 6:1–25. |
| `ToothGrowth.csv` | datasets::ToothGrowth | Crampton (1947), *J. Nutrition* 33:491–504. |
| `PlantGrowth.csv` | datasets::PlantGrowth | Dobson (1983), *An Introduction to Statistical Modelling*, Chapman & Hall. |
| `iris.csv` | datasets::iris | Anderson (1935), *Bull. American Iris Society* 59:2–5; Fisher (1936), *Annals of Eugenics* 7:179–188. |
| `faithful.csv` | datasets::faithful | Old Faithful geyser, Yellowstone. Härdle (1991); Azzalini & Bowman (1990), *Applied Statistics* 39:357–365. |
| `spam7.csv` | DAAG::spam7 | UCI Spambase (Hopkins, Reeber, Forman & Suermondt, Hewlett-Packard Labs, 1999), https://doi.org/10.24432/C53G6X. 4,601 e-mails, 6 of the 57 original features. |

The Play Tennis table in `code/q4_classification.py` is typed in from Quinlan (1986)
as printed in Mitchell (1997), *Machine Learning*, Table 3.2, with the Wind column
omitted.
