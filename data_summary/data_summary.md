# Project Data Summary

This document contains a summary of the project data, generated to provide context for an LLM. The original data is in a SQLite database and several CSV files.

## SQL Database (`cycling_big.db`) Overview

Found the following tables: riders, race_results, sqlite_sequence.

### Data Summary: SQL Table 'race_results'

**Shape:** 225918 rows, 25 columns.

**Columns and Data Types:**
- `id`: int64
- `Rnk`: object
- `GC`: float64
- `Timelag`: object
- `BiB`: object
- `Rider`: object
- `Age`: int64
- `Team`: object
- `UCI`: float64
- `Pnt`: float64
- `Time`: object
- `Circuit`: int64
- `Race_Name`: object
- `Stage_Name`: object
- `Date`: object
- `Stage_Type`: object
- `Start`: object
- `Finish`: object
- `Race_ID`: int64
- `Stage_Number`: int64
- `Length`: object
- `Category`: object
- `Race_url`: object
- `Stage_url`: object
- `rider_id`: object

**Basic Statistics (for numeric columns):**
```
                  id             GC            Age           UCI           Pnt   Circuit        Race_ID   Stage_Number
count  225918.000000  195498.000000  225918.000000  11844.000000  31760.000000  225918.0  225918.000000  225918.000000
mean   112959.500000      80.501130      28.298936     34.911770     16.463791       1.0      16.315473       6.743925
std     65217.053395      50.094816       4.270149     65.396238     27.250944       0.0       8.518667       5.736211
min         1.000000       1.000000      18.000000      1.000000      1.000000       1.0       0.000000       1.000000
25%     56480.250000      39.000000      25.000000      5.000000      5.000000       1.0      11.000000       2.000000
50%    112959.500000      78.500000      28.000000     12.000000      5.000000       1.0      17.000000       5.000000
75%    169438.750000     118.000000      31.000000     30.000000     18.000000       1.0      22.000000      10.000000
max    225918.000000    1011.000000      45.000000    500.000000    275.000000       1.0      37.000000      25.000000
```

**Top values and unique counts (for categorical/object columns):**
- `Rnk` (unique values: 370):
  - `DNF`: 12062 occurrences
  - `4`: 1396 occurrences
  - `39`: 1395 occurrences
  - `22`: 1395 occurrences
  - `13`: 1395 occurrences

- `Timelag` (unique values: 16178):
  - `+0:10`: 6318 occurrences
  - `+0:00`: 2287 occurrences
  - `+0:20`: 1065 occurrences
  - `+0:14`: 913 occurrences
  - `+0:24`: 766 occurrences

- `BiB` (unique values: 259):
  - `0`: 14624 occurrences
  - `6`: 1292 occurrences
  - `2`: 1280 occurrences
  - `36`: 1274 occurrences
  - `76`: 1272 occurrences

- `Rider` (unique values: 2107):
  - `DE GENDT Thomas`: 656 occurrences
  - `ERVITI Imanol`: 577 occurrences
  - `IZAGIRRE Gorka`: 554 occurrences
  - `HANSEN Adam`: 551 occurrences
  - `CLARKE Simon`: 544 occurrences

- `Team` (unique values: 197):
  - `Movistar Team`: 10110 occurrences
  - `Astana Pro Team`: 8953 occurrences
  - `AG2R La Mondiale`: 8772 occurrences
  - `Lotto Soudal`: 7643 occurrences
  - `BMC Racing Team`: 7038 occurrences

- `Time` (unique values: 6400):
  - `,,0:00`: 41428 occurrences
  - `-`: 13417 occurrences
  - `,,0:03`: 1678 occurrences
  - `,,0:05`: 1243 occurrences
  - `,,0:04`: 1164 occurrences

- `Race_Name` (unique values: 71):
  - `Giro d'Italia`: 32715 occurrences
  - `Tour de France`: 32691 occurrences
  - `Vuelta a España`: 18166 occurrences
  - `La Vuelta ciclista a España`: 13840 occurrences
  - `Tour de Suisse`: 11126 occurrences

- `Stage_Name` (unique values: 1155):
  - `Teams classification`: 1833 occurrences
  - `Points classification`: 1689 occurrences
  - `Mountains classification`: 1557 occurrences
  - `Stage 1 | Calella-Calella`: 1453 occurrences
  - `Youth classification`: 1416 occurrences

- `Date` (unique values: 1323):
  - `05 September 2021`: 832 occurrences
  - `16 March 2021`: 656 occurrences
  - `10 April 2021`: 616 occurrences
  - `30 May 2021`: 572 occurrences
  - `28 March 2021`: 568 occurrences

- `Stage_Type` (unique values: 2):
  - `RR`: 206130 occurrences
  - `ITT`: 19788 occurrences

- `Start` (unique values: 902):
  - `Nice`: 2162 occurrences
  - `San Benedetto del Tronto`: 1898 occurrences
  - `Liège`: 1699 occurrences
  - `Milano`: 1669 occurrences
  - `Plouay`: 1623 occurrences

- `Finish` (unique values: 884):
  - `San Benedetto del Tronto`: 1898 occurrences
  - `Barcelona`: 1744 occurrences
  - `Oudenaarde`: 1693 occurrences
  - `Sanremo`: 1687 occurrences
  - `Roubaix`: 1686 occurrences

- `Length` (unique values: 680):
  - `0 km`: 6495 occurrences
  - `184 km`: 1949 occurrences
  - `180 km`: 1829 occurrences
  - `177 km`: 1826 occurrences
  - `181 km`: 1777 occurrences

- `Category` (unique values: 1):
  - `ME - Men Elite`: 225918 occurrences

- `Race_url` (unique values: 272):
  - `race/vuelta-a-espana/2021`: 4112 occurrences
  - `race/giro-d-italia/2021`: 4093 occurrences
  - `race/tour-de-france/2016`: 3992 occurrences
  - `race/tour-de-france/2021`: 3980 occurrences
  - `race/giro-d-italia/2017`: 3860 occurrences

- `Stage_url` (unique values: 42):
  - `/stage-2/result/result`: 20105 occurrences
  - `/stage-4/result/result`: 19963 occurrences
  - `/stage-3/result/result`: 19950 occurrences
  - `/stage-5/result/result`: 19395 occurrences
  - `/stage-1/result/result`: 17418 occurrences

- `rider_id` (unique values: 979):
  - `e29bb5c9216abf48f04f4d30c00aadf4`: 656 occurrences
  - `3b8bf287f9853e5d791740f13b46c14c`: 577 occurrences
  - `8ca4cfaf07a8e357bbcfbffbf2061b25`: 554 occurrences
  - `a5a272c3f72d662fe07ad64bfc25e0b2`: 551 occurrences
  - `64ce81af9f1e95f2417c7b761426b157`: 544 occurrences

**Sample Data (First 5 rows):**
```
|   id |   Rnk |   GC | Timelag   |   BiB | Rider               |   Age | Team                  |   UCI |   Pnt | Time    |   Circuit | Race_Name              | Stage_Name               | Date            | Stage_Type   | Start    | Finish   |   Race_ID |   Stage_Number | Length   | Category       | Race_url                  | Stage_url              | rider_id                         |
|-----:|------:|-----:|:----------|------:|:--------------------|------:|:----------------------|------:|------:|:--------|----------:|:-----------------------|:-------------------------|:----------------|:-------------|:---------|:---------|----------:|---------------:|:---------|:---------------|:--------------------------|:-----------------------|:---------------------------------|
|    1 |     1 |    1 | +0:00     |     0 | GREIPEL André       |    29 | Lotto Belisol Team    |     6 |    50 | 4:33:40 |         1 | Santos Tour Down Under | Stage 1 | Prospect-Clare | 17 January 2012 | RR           | Prospect | Clare    |         0 |              1 | 149 km   | ME - Men Elite | race/tour-down-under/2012 | /stage-1/result/result | 659ed585810c65fe22255a5e4a9b7838 |
|    2 |    2  |    2 | +0:04     |     0 | PETACCHI Alessandro |    38 | Lampre - ISD          |     4 |    30 | ,,0:00  |         1 | Santos Tour Down Under | Stage 1 | Prospect-Clare | 17 January 2012 | RR           | Prospect | Clare    |         0 |              1 | 149 km   | ME - Men Elite | race/tour-down-under/2012 | /stage-1/result/result |                                  |
|    3 |     3 |    4 | +0:06     |     0 | HUTAROVICH Yauheni  |    28 | FDJ - BigMat          |     2 |    18 | ,,0:00  |         1 | Santos Tour Down Under | Stage 1 | Prospect-Clare | 17 January 2012 | RR           | Prospect | Clare    |         0 |              1 | 149 km   | ME - Men Elite | race/tour-down-under/2012 | /stage-1/result/result |                                  |
|    4 |     4 |    8 | +0:10     |     0 | SABATINI Fabio      |    26 | Liquigas - Cannondale |     1 |    13 | ,,0:00  |         1 | Santos Tour Down Under | Stage 1 | Prospect-Clare | 17 January 2012 | RR           | Prospect | Clare    |         0 |              1 | 149 km   | ME - Men Elite | race/tour-down-under/2012 | /stage-1/result/result | 13ed0fc8c2b0dcd2c4e1ac48b88166b8 |
|    5 |     5 |    9 | +0:10     |     0 | BENNATI Daniele     |    31 | RadioShack - Nissan   |     1 |    10 | ,,0:00  |         1 | Santos Tour Down Under | Stage 1 | Prospect-Clare | 17 January 2012 | RR           | Prospect | Clare    |         0 |              1 | 149 km   | ME - Men Elite | race/tour-down-under/2012 | /stage-1/result/result | c0c77a7b1a8b55d9641962ba21981cab |
```

## CSV Files Overview

Combining all CSV files into a single dataset for analysis.

### Data Summary: Combined CSV Data

**Shape:** 228325 rows, 35 columns.

**Columns and Data Types:**
- `Unnamed: 0`: int64
- `fullname`: object
- `team`: object
- `birthdate`: object
- `country`: object
- `height`: float64
- `weight`: float64
- `rider_url`: object
- `pps`: object
- `rdr`: object
- `rider_name`: object
- `Rnk`: object
- `GC`: float64
- `Timelag`: object
- `BiB`: object
- `Rider`: object
- `Age`: float64
- `Team`: object
- `UCI`: float64
- `Pnt`: float64
- `Time`: object
- `Circuit`: float64
- `Race_Name`: object
- `Stage_Name`: object
- `Date`: object
- `Stage_Type`: object
- `Start`: object
- `Finish`: object
- `Race_ID`: float64
- `Stage#`: float64
- `Length`: object
- `Category`: object
- `Race_url`: object
- `Stage_url`: object
- `team_url`: object

**Basic Statistics (for numeric columns):**
```
          Unnamed: 0       height       weight             GC            Age           UCI           Pnt   Circuit        Race_ID         Stage#
count  228325.000000  1042.000000  1042.000000  195498.000000  225918.000000  11844.000000  31760.000000  225918.0  225918.000000  225918.000000
mean    12656.135916     1.711113    63.872841      80.501130      28.298936     34.911770     16.463791       1.0      16.315473       6.743925
std      7670.688068     0.405112    18.379483      50.094816       4.270149     65.396238     27.250944       0.0       8.518667       5.736211
min         0.000000     0.000000     0.000000       1.000000      18.000000      1.000000      1.000000       1.0       0.000000       1.000000
25%      6074.000000     1.750000    63.000000      39.000000      25.000000      5.000000      5.000000       1.0      11.000000       2.000000
50%     12417.000000     1.800000    68.000000      78.500000      28.000000     12.000000      5.000000       1.0      17.000000       5.000000
75%     18960.000000     1.840000    73.000000     118.000000      31.000000     30.000000     18.000000       1.0      22.000000      10.000000
max     30030.000000     2.040000    90.000000    1011.000000      45.000000    500.000000    275.000000       1.0      37.000000      25.000000
```

**Top values and unique counts (for categorical/object columns):**
- `fullname` (unique values: 1042):
  - `DELACROIX Théo`: 1 occurrences
  - `BARDET Romain`: 1 occurrences
  - `DE CLERCQ Bart`: 1 occurrences
  - `OFFREDO Yoann`: 1 occurrences
  - `EIKING Odd Christian`: 1 occurrences

- `team` (unique values: 83):
  - `noteam`: 236 occurrences
  - `AG2R Citroën Team`: 28 occurrences
  - `Deceuninck - Quick Step`: 28 occurrences
  - `Israel Start-Up Nation`: 28 occurrences
  - `UAE-Team Emirates`: 27 occurrences

- `birthdate` (unique values: 953):
  - `1995-10-30`: 3 occurrences
  - `1995-07-01`: 3 occurrences
  - `1988-01-01`: 2 occurrences
  - `1996-07-30`: 2 occurrences
  - `1997-01-16`: 2 occurrences

- `country` (unique values: 54):
  - `France`: 149 occurrences
  - `Belgium`: 128 occurrences
  - `Italy`: 127 occurrences
  - `Spain`: 89 occurrences
  - `Netherlands`: 65 occurrences

- `rider_url` (unique values: 1042):
  - `https://www.procyclingstats.com/rider/theo-delacroix`: 2 occurrences
  - `https://www.procyclingstats.com/rider/romain-bardet`: 2 occurrences
  - `https://www.procyclingstats.com/rider/bart-de-clercq`: 2 occurrences
  - `https://www.procyclingstats.com/rider/yoann-offredo`: 2 occurrences
  - `https://www.procyclingstats.com/rider/odd-christian-eiking`: 2 occurrences

- `pps` (unique values: 1039):
  - `{'One day races': '0', 'GC': '0', 'Time trial': '0', 'Sprint': '0', 'Climber': '0'}`: 4 occurrences
  - `{'One day races': '3681', 'GC': '1277', 'Time trial': '91', 'Sprint': '6327', 'Climber': '615'}`: 1 occurrences
  - `{'One day races': '2864', 'GC': '2268', 'Time trial': '1066', 'Sprint': '1988', 'Climber': '2545'}`: 1 occurrences
  - `{'One day races': '3619', 'GC': '1157', 'Time trial': '35', 'Sprint': '1996', 'Climber': '968'}`: 1 occurrences
  - `{'One day races': '702', 'GC': '2803', 'Time trial': '604', 'Sprint': '352', 'Climber': '2386'}`: 1 occurrences

- `rdr` (unique values: 851):
  - `{}`: 192 occurrences
  - `{'PCS Ranking': '43', 'UCI World Ranking': '52', 'Specials | All Time Ranking': '375'}`: 1 occurrences
  - `{'Specials | All Time Ranking': '365'}`: 1 occurrences
  - `{'PCS Ranking': '511', 'UCI World Ranking': '999', 'Specials | All Time Ranking': '537'}`: 1 occurrences
  - `{'PCS Ranking': '203', 'UCI World Ranking': '143', 'Specials | All Time Ranking': '729'}`: 1 occurrences

- `rider_name` (unique values: 1042):
  - `DELACROIX Théo`: 1 occurrences
  - `BARDET Romain`: 1 occurrences
  - `DE CLERCQ Bart`: 1 occurrences
  - `OFFREDO Yoann`: 1 occurrences
  - `EIKING Odd Christian`: 1 occurrences

- `Rnk` (unique values: 370):
  - `DNF`: 12062 occurrences
  - `4`: 1396 occurrences
  - `39`: 1395 occurrences
  - `22`: 1395 occurrences
  - `13`: 1395 occurrences

- `Timelag` (unique values: 16178):
  - `+0:10`: 6318 occurrences
  - `+0:00`: 2287 occurrences
  - `+0:20`: 1065 occurrences
  - `+0:14`: 913 occurrences
  - `+0:24`: 766 occurrences

- `BiB` (unique values: 492):
  - `0`: 13811 occurrences
  - `0`: 813 occurrences
  - `6`: 756 occurrences
  - `5`: 755 occurrences
  - `76`: 752 occurrences

- `Rider` (unique values: 2107):
  - `DE GENDT Thomas`: 656 occurrences
  - `ERVITI Imanol`: 577 occurrences
  - `IZAGIRRE Gorka`: 554 occurrences
  - `HANSEN Adam`: 551 occurrences
  - `CLARKE Simon`: 544 occurrences

- `Team` (unique values: 197):
  - `Movistar Team`: 10110 occurrences
  - `Astana Pro Team`: 8953 occurrences
  - `AG2R La Mondiale`: 8772 occurrences
  - `Lotto Soudal`: 7643 occurrences
  - `BMC Racing Team`: 7038 occurrences

- `Time` (unique values: 6400):
  - `,,0:00`: 41428 occurrences
  - `-`: 13417 occurrences
  - `,,0:03`: 1678 occurrences
  - `,,0:05`: 1243 occurrences
  - `,,0:04`: 1164 occurrences

- `Race_Name` (unique values: 71):
  - `Giro d'Italia`: 32715 occurrences
  - `Tour de France`: 32691 occurrences
  - `Vuelta a España`: 18166 occurrences
  - `La Vuelta ciclista a España`: 13840 occurrences
  - `Tour de Suisse`: 11126 occurrences

- `Stage_Name` (unique values: 1155):
  - `Teams classification`: 1833 occurrences
  - `Points classification`: 1689 occurrences
  - `Mountains classification`: 1557 occurrences
  - `Stage 1 | Calella-Calella`: 1453 occurrences
  - `Youth classification`: 1416 occurrences

- `Date` (unique values: 1323):
  - `05 September 2021`: 832 occurrences
  - `16 March 2021`: 656 occurrences
  - `10 April 2021`: 616 occurrences
  - `30 May 2021`: 572 occurrences
  - `28 March 2021`: 568 occurrences

- `Stage_Type` (unique values: 2):
  - `RR`: 206130 occurrences
  - `ITT`: 19788 occurrences

- `Start` (unique values: 902):
  - `Nice`: 2162 occurrences
  - `San Benedetto del Tronto`: 1898 occurrences
  - `Liège`: 1699 occurrences
  - `Milano`: 1669 occurrences
  - `Plouay`: 1623 occurrences

- `Finish` (unique values: 884):
  - `San Benedetto del Tronto`: 1898 occurrences
  - `Barcelona`: 1744 occurrences
  - `Oudenaarde`: 1693 occurrences
  - `Sanremo`: 1687 occurrences
  - `Roubaix`: 1686 occurrences

- `Length` (unique values: 680):
  - `0 km`: 6495 occurrences
  - `184 km`: 1949 occurrences
  - `180 km`: 1829 occurrences
  - `177 km`: 1826 occurrences
  - `181 km`: 1777 occurrences

- `Category` (unique values: 1):
  - `ME - Men Elite`: 225918 occurrences

- `Race_url` (unique values: 272):
  - `race/vuelta-a-espana/2021`: 4112 occurrences
  - `race/giro-d-italia/2021`: 4093 occurrences
  - `race/tour-de-france/2016`: 3992 occurrences
  - `race/tour-de-france/2021`: 3980 occurrences
  - `race/giro-d-italia/2017`: 3860 occurrences

- `Stage_url` (unique values: 42):
  - `/stage-2/result/result`: 20105 occurrences
  - `/stage-4/result/result`: 19963 occurrences
  - `/stage-3/result/result`: 19950 occurrences
  - `/stage-5/result/result`: 19395 occurrences
  - `/stage-1/result/result`: 17418 occurrences

- `team_url` (unique values: 323):
  - `https://www.procyclingstats.com/team/wanty-gobert-cycling-team-2019`: 1 occurrences
  - `https://www.procyclingstats.com/team/ag2r-la-mondiale-2012`: 1 occurrences
  - `https://www.procyclingstats.com/team/astana-pro-team-2012`: 1 occurrences
  - `https://www.procyclingstats.com/team/gazprom-rusvelo-2019`: 1 occurrences
  - `https://www.procyclingstats.com/team/euskadi-basque-country-murias-2019`: 1 occurrences

**Sample Data (First 5 rows):**
```
|   Unnamed: 0 | fullname        | team              | birthdate   | country     |   height |   weight | rider_url                                             | pps                                                                                                | rdr                                                                                       |   rider_name |   Rnk |   GC |   Timelag |   BiB |   Rider |   Age |   Team |   UCI |   Pnt |   Time |   Circuit |   Race_Name |   Stage_Name |   Date |   Stage_Type |   Start |   Finish |   Race_ID |   Stage# |   Length |   Category |   Race_url |   Stage_url |   team_url |
|-------------:|:----------------|:------------------|:------------|:------------|---------:|---------:|:------------------------------------------------------|:---------------------------------------------------------------------------------------------------|:------------------------------------------------------------------------------------------|-------------:|------:|-----:|----------:|------:|--------:|------:|-------:|------:|------:|-------:|----------:|------------:|-------------:|-------:|-------------:|--------:|---------:|----------:|---------:|---------:|-----------:|-----------:|------------:|-----------:|
|            0 | BARDET Romain   | Team DSM          | 1990-11-09  | France      |     1.84 |       65 | https://www.procyclingstats.com/rider/romain-bardet   | {'One day races': '2620', 'GC': '5138', 'Time trial': '333', 'Sprint': '446', 'Climber': '6414'}   | {'PCS Ranking': '43', 'UCI World Ranking': '52', 'Specials | All Time Ranking': '375'}    |          nan |   nan |  nan |       nan |   nan |     nan |   nan |    nan |   nan |   nan |    nan |       nan |         nan |          nan |    nan |          nan |     nan |      nan |       nan |      nan |      nan |        nan |        nan |         nan |        nan |
|            1 | DUMOULIN Samuel | noteam            | 1980-08-20  | France      |     1.59 |       57 | https://www.procyclingstats.com/rider/samuel-dumoulin | {'One day races': '3681', 'GC': '1277', 'Time trial': '91', 'Sprint': '6327', 'Climber': '615'}    | {'Specials | All Time Ranking': '365'}                                                    |          nan |   nan |  nan |       nan |   nan |     nan |   nan |    nan |   nan |   nan |    nan |       nan |         nan |          nan |    nan |          nan |     nan |      nan |       nan |      nan |      nan |        nan |        nan |         nan |        nan |
|            2 | GALLOPIN Tony   | AG2R Citroën Team | 1988-05-24  | France      |     1.8  |       69 | https://www.procyclingstats.com/rider/tony-gallopin   | {'One day races': '2864', 'GC': '2268', 'Time trial': '1066', 'Sprint': '1988', 'Climber': '2545'} | {'PCS Ranking': '511', 'UCI World Ranking': '999', 'Specials | All Time Ranking': '537'}  |          nan |   nan |  nan |       nan |   nan |     nan |   nan |    nan |   nan |   nan |    nan |       nan |         nan |          nan |    nan |          nan |     nan |      nan |       nan |      nan |      nan |        nan |        nan |         nan |        nan |
|            3 | NAESEN Oliver   | AG2R Citroën Team | 1990-09-16  | Belgium     |     1.84 |       72 | https://www.procyclingstats.com/rider/oliver-naesen   | {'One day races': '3619', 'GC': '1157', 'Time trial': '35', 'Sprint': '1996', 'Climber': '968'}    | {'PCS Ranking': '203', 'UCI World Ranking': '143', 'Specials | All Time Ranking': '729'}  |          nan |   nan |  nan |       nan |   nan |     nan |   nan |    nan |   nan |   nan |    nan |       nan |         nan |          nan |    nan |          nan |     nan |      nan |       nan |      nan |      nan |        nan |        nan |         nan |        nan |
|            4 | FRANK Mathias   | noteam            | 1986-12-09  | Switzerland |     1.76 |       64 | https://www.procyclingstats.com/rider/mathias-frank   | {'One day races': '702', 'GC': '2803', 'Time trial': '604', 'Sprint': '352', 'Climber': '2386'}    | {'PCS Ranking': '755', 'UCI World Ranking': '902', 'Specials | All Time Ranking': '1235'} |          nan |   nan |  nan |       nan |   nan |     nan |   nan |    nan |   nan |   nan |    nan |       nan |         nan |          nan |    nan |          nan |     nan |      nan |       nan |      nan |      nan |        nan |        nan |         nan |        nan |
```

