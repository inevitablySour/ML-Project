# Project Data Summary & Analysis

This document contains an automated analysis of the project data, focusing on quality, structure, and strategic insights for rider evaluation.

### Data Summary: SQL Table 'race_results'

**Shape:** 225918 rows, 25 columns.

**Columns and Data Types:**
|              | Data Type   |
|:-------------|:------------|
| id           | int64       |
| Rnk          | object      |
| GC           | float64     |
| Timelag      | object      |
| BiB          | object      |
| Rider        | object      |
| Age          | int64       |
| Team         | object      |
| UCI          | float64     |
| Pnt          | float64     |
| Time         | object      |
| Circuit      | int64       |
| Race_Name    | object      |
| Stage_Name   | object      |
| Date         | object      |
| Stage_Type   | object      |
| Start        | object      |
| Finish       | object      |
| Race_ID      | int64       |
| Stage_Number | int64       |
| Length       | object      |
| Category     | object      |
| Race_url     | object      |
| Stage_url    | object      |
| rider_id     | object      |

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

### Data Summary: CSV File 'rider_infos.csv'

**Shape:** 1042 rows, 10 columns.

**Columns and Data Types:**
|            | Data Type   |
|:-----------|:------------|
| Unnamed: 0 | int64       |
| fullname   | object      |
| team       | object      |
| birthdate  | object      |
| country    | object      |
| height     | float64     |
| weight     | float64     |
| rider_url  | object      |
| pps        | object      |
| rdr        | object      |

**Basic Statistics (for numeric columns):**
```
        Unnamed: 0       height       weight
count  1042.000000  1042.000000  1042.000000
mean    520.500000     1.711113    63.872841
std     300.943793     0.405112    18.379483
min       0.000000     0.000000     0.000000
25%     260.250000     1.750000    63.000000
50%     520.500000     1.800000    68.000000
75%     780.750000     1.840000    73.000000
max    1041.000000     2.040000    90.000000
```


---
## Data Dictionary & Context

This section explains each column in the unified dataset, providing context on its meaning and programmatically-verified quality notes.

| Column | Description | Data Type | Notes |
|:---|:---|:---|:---|
| `id` | A unique row identifier from the original SQL `race_results` table. | `int64` | OK |
| `Rnk` | The rider's finishing position (rank) for that specific stage. | `object` | Needs cleaning/parsing |
| `GC` | General Classification: The rider's overall rank in a multi-day tour based on cumulative time. | `float64` | 13.5% missing |
| `Timelag` | How far behind the stage winner the rider finished. | `object` | 13.5% missing, Needs cleaning/parsing |
| `BiB` | The rider's bib number for the race. | `object` | OK |
| `Rider` | The full name of the cyclist. This is the key for merging datasets. | `object` | OK |
| `Age` | The rider's age at the time the `race_results` data was collected. | `int64` | OK |
| `Team` | The professional team the rider was on for that specific race. | `object` | 0.0% missing |
| `UCI` | Points awarded by the UCI for that specific race. | `float64` | 94.8% missing |
| `Pnt` | An alternative points metric for a race result. | `float64` | 85.9% missing |
| `Time` | The rider's finishing time for the stage. | `object` | Needs cleaning/parsing |
| `Circuit` | A column with only one value; provides no predictive information. | `int64` | Constant value (useless for prediction) |
| `Race_Name` | The name of the overall event (e.g., Tour de France). | `object` | OK |
| `Stage_Name` | A description of the stage, often the start and end cities. | `object` | 11.2% missing |
| `Date` | The date the race stage took place. | `object` | OK |
| `Stage_Type` | The format of the race: RR (Road Race) or ITT (Individual Time Trial). | `object` | OK |
| `Start` | The start city/location of the stage. | `object` | OK |
| `Finish` | The finish city/location of the stage. | `object` | OK |
| `Race_ID` | A unique identifier for the overall race event. | `int64` | OK |
| `Stage_Number` | The specific day or stage number of a multi-day tour. | `int64` | OK |
| `Length` | The length of the stage. | `object` | Needs cleaning/parsing |
| `Category` | A column with only one value ("ME - Men Elite"). | `object` | Constant value (useless for prediction) |
| `Race_url` | A URL slug for the race page on ProCyclingStats. | `object` | Can likely be dropped |
| `Stage_url` | A URL slug for the stage page on ProCyclingStats. | `object` | 11.2% missing, Can likely be dropped |
| `rider_id` | A unique hash identifier for the rider from the `race_results` table. | `object` | 23.1% missing |
| `Unnamed: 0` | An index column from the `rider_infos.csv` file. | `float64` | 23.1% missing, Can likely be dropped |
| `team` | The rider's team at the time the `rider_infos.csv` data was collected. | `object` | 23.1% missing |
| `birthdate` | The rider's date of birth. | `object` | 23.1% missing |
| `country` | The nationality of the rider. | `object` | 23.1% missing |
| `height` | The rider's height in meters. | `float64` | 23.1% missing |
| `weight` | The rider's weight in kilograms. | `float64` | 23.1% missing |
| `rider_url` | The full URL for the rider's page on ProCyclingStats. | `object` | 23.1% missing, Can likely be dropped |
| `pps` | A raw string from ProCyclingStats containing rider skill scores (e.g., Climber, Sprint). | `object` | 23.1% missing |
| `rdr` | A raw string from ProCyclingStats containing rider world rankings (e.g., PCS Ranking). | `object` | 23.1% missing |

---
## Action Plan: Data Cleaning & Preparation

This analysis reveals several critical data quality issues. The following is a recommended action plan based on programmatic checks of the data.

### 1. Filter Irrelevant Rows
- **Diagnosis:** Found **6495 rows** where `Stage_Name` contains keywords like 'classification', indicating they are summary rows, not actual race results.
- **Action:** Filter out these rows to ensure the model is only trained on rider performances in specific stages.

### 2. Clean and Format Key Columns
- **Diagnosis:** Crucial columns are stored as text and contain non-numeric characters.
- **Action Plan (based on checks):**
  - **`Rnk`**: Found **14424 non-numeric entries** (like 'DNF'). These must be converted to a high integer (e.g., 999).
  - **`Length`**: Found **225918 entries** containing 'km'. This text must be removed and the column converted to numeric.
  - **`Date` / `birthdate`**: These are stored as objects and must be converted to datetime objects for calculations like `age_at_race`.
### 3. Address Missing Data
- **Diagnosis:** Some columns have sporadic or extreme missingness.
- **Action Plan (based on checks):**
  - **Drop `UCI`**: This column is **94.8% empty** and unusable.
  - **Drop `Pnt`**: This column is **85.9% empty** and unusable.
  - **Impute `GC`**: This column has sporadic missing values that should be filled using a reasonable strategy (e.g., median).
  - **Impute `height`**: This column has sporadic missing values that should be filled using a reasonable strategy (e.g., median).
  - **Impute `weight`**: This column has sporadic missing values that should be filled using a reasonable strategy (e.g., median).
### 4. Engineer & Finalize Features
- **Diagnosis:** Valuable data is locked in strings, and some columns are redundant.
- **Action Plan (based on checks):**
  - **Parse `pps` and `rdr`**: These columns contain dictionary-like strings with vital rider skill and ranking data that must be extracted into new features.
  - **Create `is_top_10`**: A new target variable should be created from the cleaned `Rnk` column.
  - **Drop Constant Columns**: The following columns have only one unique value and are useless for prediction: `Circuit, Category`.

---
## Strategic Insights for Rider Recruitment

This analysis answers key business questions for CAICLE by identifying rider archetypes, consistent performers, and career patterns.

### 1. Rider Archetype Analysis

**Top 5 Identified Climbers:**
| Rider              |   Climber_Score |
|:-------------------|----------------:|
| VALVERDE Alejandro |           16783 |
| NIBALI Vincenzo    |            9554 |
| MOLLEMA Bauke      |            7852 |
| MARTIN Dan         |            7604 |
| QUINTANA Nairo     |            7457 |

**Top 5 Identified Sprinters:**
| Rider              |   Sprint_Score |
|:-------------------|---------------:|
| GREIPEL André      |          15910 |
| CAVENDISH Mark     |          14486 |
| SAGAN Peter        |          14148 |
| KRISTOFF Alexander |          11466 |
| BOUHANNI Nacer     |           9337 |

This data is crucial for identifying specialists to build a balanced team.

### 2. Performance and Career Arc Insights

**Most Consistent Top Performers (min. 50 races):**
| Rider                |   total_races |   top_10_finishes |   top_10_rate |
|:---------------------|--------------:|------------------:|--------------:|
| POGAČAR Tadej        |           138 |                67 |         48.55 |
| VAN DER POEL Mathieu |            57 |                27 |         47.37 |
| SAGAN Peter          |           521 |               237 |         45.49 |
| VAN AERT Wout        |           115 |                51 |         44.35 |
| ALMEIDA João         |           103 |                45 |         43.69 |

The average age of a top-10 finisher in this dataset is **27.3 years old**, suggesting a rider's peak performance window.

### 3. Race Importance and Context

The top 5 most frequent (and likely most important 'Tier 1') races are:
| Race_Name                   |   Number of Rider Results |
|:----------------------------|--------------------------:|
| Giro d'Italia               |                     32715 |
| Tour de France              |                     32691 |
| Vuelta a España             |                     18166 |
| La Vuelta ciclista a España |                     13840 |
| Tour de Suisse              |                     11126 |

A rider's performance in these key events should be weighted more heavily.

