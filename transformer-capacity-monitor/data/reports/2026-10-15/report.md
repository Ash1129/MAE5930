# Transformer capacity monitoring report, period ending 2026-10-15

Status: **DRAFT** (not yet finalized by a reviewer)

- Period: 2026-10-09 to 2026-10-15 (7 days); chart history from 2026-08-16
- Run: 2026-10-15_20261017T013850923_manual (reruns of this period: 9)
- Playbook version: default-2026-10-17
- Generated: 2026-10-17T01:38:58-04:00

## Summary

| Transformers | Within limits | Review needed | Inspect now | Stable | Chart signal | Insufficient history |
|---|---|---|---|---|---|---|
| 500 | 381 | 97 | 22 | 439 | 52 | 9 |

Exceptions with a recorded disposition: 0 of 119

## Sources

- readings: `C:\Users\deep\MAE5930\transformer-capacity-monitor\data\feeds\readings.csv` (886392 rows, sha256 420ef28b849ede78, modified 2026-10-17T01:38:36)
- assets: `C:\Users\deep\MAE5930\transformer-capacity-monitor\data\feeds\assets.csv` (500 rows, sha256 fadb36eb6b2d0f8b, modified 2026-10-17T01:38:36)
- boundaries: `C:\Users\deep\MAE5930\transformer-capacity-monitor\data\feeds\boundaries.geojson` (12 rows, sha256 0989c623df36b289, modified 2026-10-17T01:38:36)
- forecast: `C:\Users\deep\MAE5930\transformer-capacity-monitor\data\feeds\heat_pump_forecast.csv` (24 rows, sha256 9f2212e4c89d9bb8, modified 2026-10-17T01:38:36)

## Transformers

| Transformer | Area | Rated max | Period peak | Stability | Cpk (95% CI) | Projected peak | Status | Disposition |
|---|---|---|---|---|---|---|---|---|
| T-CAR-006 Slaterville Rd pole | Town of Caroline (CAR) | 100.0 kVA | 73.3 | stable | 2.75 (2.12 to 3.38) | 141.5 | review_needed | - |
| T-CAR-101 Pine Tree Rd pole | Town of Caroline (CAR) | 75.0 kVA | 62.8 | stable | 0.88 (0.67 to 1.10) | 91.2 | review_needed | - |
| T-CAR-102 Orchard Rd pad | Town of Caroline (CAR) | 167.0 kVA | 110.7 | stable | 3.14 (2.42 to 3.86) | 172.1 | review_needed | - |
| T-CAR-103 Cemetery Rd pad | Town of Caroline (CAR) | 333.0 kVA | 222.6 | stable | 3.34 (2.58 to 4.10) | 351.1 | review_needed | - |
| T-CAR-104 Pine Tree Rd pad | Town of Caroline (CAR) | 167.0 kVA | 171.3 | signal | not calculated | - | inspect_now | - |
| T-CAR-105 Pine Tree Rd pole | Town of Caroline (CAR) | 50.0 kVA | 32.4 | stable | 3.19 (2.46 to 3.92) | 50.6 | review_needed | - |
| T-CAR-106 Maple Ave pad | Town of Caroline (CAR) | 100.0 kVA | 64.7 | stable | 3.35 (2.58 to 4.11) | 117.0 | review_needed | - |
| T-CAR-107 Station Rd pole | Town of Caroline (CAR) | 75.0 kVA | 53.8 | stable | 2.92 (2.25 to 3.59) | 79.9 | review_needed | - |
| T-CAR-108 Church St pad | Town of Caroline (CAR) | 333.0 kVA | 283.9 | stable | 1.08 (0.82 to 1.34) | 445.4 | review_needed | - |
| T-CAR-109 Orchard Rd pad | Town of Caroline (CAR) | 100.0 kVA | 82.0 | signal | not calculated | - | review_needed | - |
| T-CAR-110 Pine Tree Rd pad | Town of Caroline (CAR) | 100.0 kVA | 65.8 | stable | 2.70 (2.08 to 3.32) | 103.3 | review_needed | - |
| T-CAR-111 Valley Rd pole | Town of Caroline (CAR) | 75.0 kVA | 47.7 | stable | 3.76 (2.91 to 4.62) | 88.6 | review_needed | - |
| T-CAR-112 Hollow Rd pad | Town of Caroline (CAR) | 100.0 kVA | 67.7 | stable | 2.47 (1.90 to 3.04) | 100.6 | review_needed | - |
| T-CAR-113 Hollow Rd pole | Town of Caroline (CAR) | 37.5 kVA | 26.3 | stable | 3.13 (2.42 to 3.85) | 43.3 | review_needed | - |
| T-CAR-114 Pine Tree Rd pad | Town of Caroline (CAR) | 167.0 kVA | 109.0 | stable | 3.05 (2.35 to 3.75) | 186.3 | review_needed | - |
| T-CAR-115 Main St pole | Town of Caroline (CAR) | 25.0 kVA | 16.6 | stable | 3.27 (2.52 to 4.02) | 24.5 | review_needed | - |
| T-CAR-116 Station Rd pole | Town of Caroline (CAR) | 37.5 kVA | 24.0 | stable | 2.80 (2.16 to 3.44) | 41.0 | review_needed | - |
| T-CAR-117 Hollow Rd pad | Town of Caroline (CAR) | 100.0 kVA | 65.6 | stable | 3.46 (2.67 to 4.25) | 99.7 | review_needed | - |
| T-CAR-118 Brook Rd pad | Town of Caroline (CAR) | 100.0 kVA | 63.3 | insufficient_history | not calculated | - | review_needed | - |
| T-CAR-119 Orchard Rd pole | Town of Caroline (CAR) | 50.0 kVA | 33.1 | stable | 3.72 (2.87 to 4.57) | 54.7 | review_needed | - |
| T-CAR-120 Brook Rd pad | Town of Caroline (CAR) | 100.0 kVA | 62.5 | stable | 3.46 (2.67 to 4.25) | 96.6 | review_needed | - |
| T-CAR-121 Lake Rd pole | Town of Caroline (CAR) | 50.0 kVA | 32.3 | stable | 2.99 (2.31 to 3.67) | 52.8 | review_needed | - |
| T-CAR-122 Elm St pole | Town of Caroline (CAR) | 75.0 kVA | 49.0 | stable | 2.83 (2.18 to 3.47) | 81.9 | review_needed | - |
| T-CAR-123 Elm St pole | Town of Caroline (CAR) | 50.0 kVA | 31.6 | stable | 2.66 (2.05 to 3.27) | 51.0 | review_needed | - |
| T-CAR-124 School Rd pole | Town of Caroline (CAR) | 25.0 kVA | 16.0 | stable | 3.48 (2.69 to 4.28) | 25.1 | review_needed | - |
| T-CAY-003 Hanshaw Rd pad | Village of Cayuga Heights (CAY-V) | 100.0 kVA | 65.5 | stable | 2.87 (2.21 to 3.53) | 74.6 | within_limits | - |
| T-CAY-101 Lake Rd pole | Village of Cayuga Heights (CAY-V) | 50.0 kVA | 32.1 | stable | 3.56 (2.75 to 4.37) | 36.6 | within_limits | - |
| T-CAY-102 Maple Ave pole | Village of Cayuga Heights (CAY-V) | 75.0 kVA | 49.4 | stable | 3.14 (2.42 to 3.86) | 53.8 | within_limits | - |
| T-CAY-103 Ridge Rd pad | Village of Cayuga Heights (CAY-V) | 100.0 kVA | 78.5 | stable | 1.70 (1.31 to 2.10) | 84.6 | review_needed | - |
| T-CAY-104 Forest Home Dr pad | Village of Cayuga Heights (CAY-V) | 250.0 kVA | 161.7 | stable | 3.29 (2.54 to 4.04) | 180.6 | within_limits | - |
| T-CAY-105 Orchard Rd pole | Village of Cayuga Heights (CAY-V) | 37.5 kVA | 23.1 | stable | 4.09 (3.16 to 5.02) | 25.9 | within_limits | - |
| T-CAY-106 Forest Home Dr pole | Village of Cayuga Heights (CAY-V) | 37.5 kVA | 24.6 | stable | 3.88 (3.00 to 4.77) | 27.7 | within_limits | - |
| T-CAY-107 Valley Rd pad | Village of Cayuga Heights (CAY-V) | 167.0 kVA | 113.3 | stable | 3.86 (2.98 to 4.74) | 123.2 | within_limits | - |
| T-CAY-108 Hollow Rd pole | Village of Cayuga Heights (CAY-V) | 25.0 kVA | 17.4 | stable | 3.24 (2.50 to 3.98) | 19.7 | within_limits | - |
| T-CAY-109 Mill St pole | Village of Cayuga Heights (CAY-V) | 50.0 kVA | 32.7 | stable | 3.45 (2.66 to 4.24) | 36.7 | within_limits | - |
| T-CAY-110 Hill Rd pad | Village of Cayuga Heights (CAY-V) | 100.0 kVA | 67.3 | stable | 2.57 (1.98 to 3.16) | 73.0 | within_limits | - |
| T-CAY-111 Hollow Rd pole | Village of Cayuga Heights (CAY-V) | 50.0 kVA | 33.6 | stable | 3.23 (2.49 to 3.97) | 37.5 | within_limits | - |
| T-CAY-112 Main St pole | Village of Cayuga Heights (CAY-V) | 37.5 kVA | 24.1 | stable | 3.47 (2.67 to 4.26) | 26.4 | within_limits | - |
| T-CAY-113 Station Rd pole | Village of Cayuga Heights (CAY-V) | 50.0 kVA | 33.6 | stable | 3.57 (2.75 to 4.38) | 38.4 | within_limits | - |
| T-CAY-114 Main St pole | Village of Cayuga Heights (CAY-V) | 75.0 kVA | 67.4 | stable | 1.25 (0.95 to 1.54) | 74.5 | review_needed | - |
| T-CAY-115 Main St pad | Village of Cayuga Heights (CAY-V) | 167.0 kVA | 105.5 | stable | 3.09 (2.38 to 3.79) | 119.0 | within_limits | - |
| T-CAY-116 Falls Rd pole | Village of Cayuga Heights (CAY-V) | 25.0 kVA | 17.2 | stable | 3.29 (2.54 to 4.05) | 18.8 | within_limits | - |
| T-CAY-117 Maple Ave pole | Village of Cayuga Heights (CAY-V) | 75.0 kVA | 48.8 | stable | 2.80 (2.16 to 3.44) | 53.4 | within_limits | - |
| T-CAY-118 Hanshaw Rd pad | Village of Cayuga Heights (CAY-V) | 100.0 kVA | 67.5 | stable | 3.23 (2.49 to 3.97) | 74.4 | within_limits | - |
| T-CAY-119 Main St pole | Village of Cayuga Heights (CAY-V) | 75.0 kVA | 50.9 | stable | 3.28 (2.53 to 4.03) | 57.5 | within_limits | - |
| T-DAN-010 Comfort Rd pole | Town of Danby (DAN) | 50.0 kVA | 46.3 | stable | 1.15 (0.87 to 1.42) | 50.7 | review_needed | - |
| T-DAN-101 Hollow Rd pad | Town of Danby (DAN) | 167.0 kVA | 136.9 | signal | not calculated | - | review_needed | - |
| T-DAN-102 Hill Rd pole | Town of Danby (DAN) | 75.0 kVA | 48.8 | stable | 2.98 (2.29 to 3.66) | 54.7 | within_limits | - |
| T-DAN-103 Orchard Rd pad | Town of Danby (DAN) | 100.0 kVA | 66.1 | stable | 3.44 (2.66 to 4.23) | 76.0 | within_limits | - |
| T-DAN-104 Maple Ave pad | Town of Danby (DAN) | 100.0 kVA | 61.9 | stable | 3.04 (2.35 to 3.74) | 68.9 | within_limits | - |
| T-DAN-105 Falls Rd pole | Town of Danby (DAN) | 25.0 kVA | 16.6 | stable | 3.55 (2.74 to 4.36) | 18.4 | within_limits | - |
| T-DAN-106 Falls Rd pole | Town of Danby (DAN) | 75.0 kVA | 50.3 | stable | 3.53 (2.72 to 4.34) | 55.4 | within_limits | - |
| T-DAN-107 Creek Rd pad | Town of Danby (DAN) | 100.0 kVA | 63.8 | stable | 3.39 (2.62 to 4.17) | 70.3 | within_limits | - |
| T-DAN-108 Orchard Rd pole | Town of Danby (DAN) | 75.0 kVA | 49.7 | stable | 3.26 (2.52 to 4.01) | 54.1 | within_limits | - |
| T-DAN-109 Mill St pole | Town of Danby (DAN) | 75.0 kVA | 51.4 | stable | 2.46 (1.89 to 3.02) | 56.0 | within_limits | - |
| T-DAN-110 School Rd pad | Town of Danby (DAN) | 100.0 kVA | 82.0 | signal | not calculated | - | review_needed | - |
| T-DAN-111 Ridge Rd pole | Town of Danby (DAN) | 37.5 kVA | 39.6 | signal | not calculated | - | inspect_now | - |
| T-DAN-112 School Rd pole | Town of Danby (DAN) | 75.0 kVA | 61.5 | signal | not calculated | - | inspect_now | - |
| T-DAN-113 Hill Rd pole | Town of Danby (DAN) | 50.0 kVA | 44.4 | stable | 1.11 (0.85 to 1.38) | 47.6 | review_needed | - |
| T-DAN-114 Falls Rd pole | Town of Danby (DAN) | 75.0 kVA | 45.3 | insufficient_history | not calculated | - | review_needed | - |
| T-DAN-115 Ridge Rd pole | Town of Danby (DAN) | 50.0 kVA | 34.5 | stable | 2.74 (2.11 to 3.36) | 38.6 | within_limits | - |
| T-DAN-116 Hollow Rd pad | Town of Danby (DAN) | 167.0 kVA | 107.5 | stable | 3.68 (2.84 to 4.52) | 123.4 | within_limits | - |
| T-DAN-117 Forest Home Dr pole | Town of Danby (DAN) | 50.0 kVA | 32.2 | stable | 2.87 (2.21 to 3.52) | 35.7 | within_limits | - |
| T-DAN-118 Mill St pole | Town of Danby (DAN) | 50.0 kVA | 32.0 | stable | 3.59 (2.77 to 4.41) | 35.7 | within_limits | - |
| T-DAN-119 Mill St pole | Town of Danby (DAN) | 75.0 kVA | 52.8 | stable | 3.03 (2.33 to 3.72) | 58.5 | within_limits | - |
| T-DAN-120 Lake Rd pole | Town of Danby (DAN) | 50.0 kVA | 41.0 | signal | not calculated | - | review_needed | - |
| T-DAN-121 Valley Rd pole | Town of Danby (DAN) | 75.0 kVA | 52.5 | stable | 3.41 (2.63 to 4.20) | 56.9 | within_limits | - |
| T-DAN-122 Ridge Rd pad | Town of Danby (DAN) | 100.0 kVA | 69.6 | stable | 2.78 (2.14 to 3.41) | 78.1 | within_limits | - |
| T-DAN-123 Station Rd pole | Town of Danby (DAN) | 75.0 kVA | 53.2 | stable | 2.79 (2.15 to 3.43) | 57.6 | within_limits | - |
| T-DAN-124 Brook Rd pole | Town of Danby (DAN) | 50.0 kVA | 41.0 | signal | not calculated | - | inspect_now | - |
| T-DAN-125 Creek Rd pad | Town of Danby (DAN) | 167.0 kVA | 106.0 | stable | 3.16 (2.44 to 3.89) | 119.1 | within_limits | - |
| T-DAN-126 Mill St pole | Town of Danby (DAN) | 50.0 kVA | 32.8 | stable | 3.22 (2.48 to 3.96) | 36.2 | within_limits | - |
| T-DAN-127 Hanshaw Rd pad | Town of Danby (DAN) | 250.0 kVA | 174.8 | stable | 2.39 (1.84 to 2.94) | 192.0 | within_limits | - |
| T-DAN-128 Falls Rd pole | Town of Danby (DAN) | 75.0 kVA | 53.6 | stable | 2.94 (2.27 to 3.61) | 59.1 | within_limits | - |
| T-DAN-129 Forest Home Dr pole | Town of Danby (DAN) | 75.0 kVA | 49.4 | stable | 3.34 (2.58 to 4.11) | 55.9 | within_limits | - |
| T-DAN-130 Elm St pole | Town of Danby (DAN) | 75.0 kVA | 47.9 | stable | 3.34 (2.57 to 4.10) | 54.7 | within_limits | - |
| T-DAN-131 School Rd pole | Town of Danby (DAN) | 25.0 kVA | 17.9 | stable | 2.53 (1.95 to 3.11) | 20.0 | within_limits | - |
| T-DAN-132 Creek Rd pad | Town of Danby (DAN) | 250.0 kVA | 164.0 | stable | 3.37 (2.60 to 4.14) | 183.6 | within_limits | - |
| T-DRY-004 Freeville Rd pole | Town of Dryden (DRY) | 75.0 kVA | 61.5 | signal | not calculated | - | review_needed | - |
| T-DRY-101 Main St pole | Town of Dryden (DRY) | 75.0 kVA | 48.5 | stable | 3.13 (2.41 to 3.85) | 53.0 | within_limits | - |
| T-DRY-102 Main St pad | Town of Dryden (DRY) | 167.0 kVA | 113.5 | stable | 3.22 (2.48 to 3.95) | 128.2 | within_limits | - |
| T-DRY-103 Main St pole | Town of Dryden (DRY) | 37.5 kVA | 24.8 | stable | 3.06 (2.36 to 3.76) | 28.3 | within_limits | - |
| T-DRY-104 Mill St pole | Town of Dryden (DRY) | 50.0 kVA | 36.6 | stable | 2.55 (1.97 to 3.14) | 40.8 | within_limits | - |
| T-DRY-105 Orchard Rd pad | Town of Dryden (DRY) | 500.0 kVA | 325.7 | stable | 3.41 (2.63 to 4.19) | 355.4 | within_limits | - |
| T-DRY-106 Elm St pole | Town of Dryden (DRY) | 75.0 kVA | 49.9 | stable | 3.62 (2.79 to 4.44) | 55.7 | within_limits | - |
| T-DRY-107 Elm St pad | Town of Dryden (DRY) | 100.0 kVA | 79.5 | stable | 1.68 (1.29 to 2.07) | 85.2 | review_needed | - |
| T-DRY-108 Hanshaw Rd pad | Town of Dryden (DRY) | 100.0 kVA | 66.1 | stable | 3.22 (2.48 to 3.95) | 72.3 | within_limits | - |
| T-DRY-109 Cemetery Rd pad | Town of Dryden (DRY) | 100.0 kVA | 70.8 | stable | 3.47 (2.68 to 4.27) | 76.5 | within_limits | - |
| T-DRY-110 School Rd pole | Town of Dryden (DRY) | 75.0 kVA | 49.3 | stable | 3.12 (2.41 to 3.84) | 54.4 | within_limits | - |
| T-DRY-111 Hollow Rd pad | Town of Dryden (DRY) | 100.0 kVA | 75.8 | stable | 1.43 (1.09 to 1.77) | 84.1 | review_needed | - |
| T-DRY-112 Maple Ave pole | Town of Dryden (DRY) | 37.5 kVA | 25.2 | stable | 2.96 (2.28 to 3.64) | 28.6 | within_limits | - |
| T-DRY-113 Ridge Rd pole | Town of Dryden (DRY) | 25.0 kVA | 17.1 | stable | 2.95 (2.27 to 3.62) | 18.6 | within_limits | - |
| T-DRY-114 Elm St pole | Town of Dryden (DRY) | 75.0 kVA | 49.6 | stable | 3.26 (2.51 to 4.00) | 56.0 | within_limits | - |
| T-DRY-115 Hill Rd pad | Town of Dryden (DRY) | 100.0 kVA | 68.5 | stable | 3.04 (2.34 to 3.73) | 78.0 | within_limits | - |
| T-DRY-116 Lake Rd pole | Town of Dryden (DRY) | 50.0 kVA | 43.5 | stable | 0.94 (0.71 to 1.17) | 48.1 | review_needed | - |
| T-DRY-117 Lake Rd pad | Town of Dryden (DRY) | 250.0 kVA | 158.2 | stable | 3.06 (2.36 to 3.77) | 176.6 | within_limits | - |
| T-DRY-118 Orchard Rd pole | Town of Dryden (DRY) | 75.0 kVA | 51.8 | stable | 2.67 (2.06 to 3.28) | 56.2 | within_limits | - |
| T-DRY-119 Elm St pole | Town of Dryden (DRY) | 50.0 kVA | 33.3 | stable | 3.57 (2.75 to 4.38) | 37.1 | within_limits | - |
| T-DRY-120 Creek Rd pole | Town of Dryden (DRY) | 50.0 kVA | 32.6 | stable | 3.57 (2.76 to 4.39) | 36.7 | within_limits | - |
| T-DRY-121 Hill Rd pad | Town of Dryden (DRY) | 333.0 kVA | 220.2 | stable | 2.87 (2.21 to 3.53) | 250.1 | within_limits | - |
| T-DRY-122 Creek Rd pad | Town of Dryden (DRY) | 250.0 kVA | 158.1 | stable | 3.66 (2.82 to 4.49) | 175.3 | within_limits | - |
| T-DRY-123 Brook Rd pad | Town of Dryden (DRY) | 100.0 kVA | 82.5 | stable | 1.31 (1.00 to 1.62) | 88.5 | review_needed | - |
| T-DRY-124 Maple Ave pad | Town of Dryden (DRY) | 250.0 kVA | 179.0 | stable | 2.69 (2.07 to 3.31) | 197.2 | within_limits | - |
| T-DRY-125 Creek Rd pole | Town of Dryden (DRY) | 75.0 kVA | 61.0 | stable | 0.88 (0.66 to 1.10) | 66.1 | review_needed | - |
| T-DRY-126 Hill Rd pole | Town of Dryden (DRY) | 75.0 kVA | 49.1 | stable | 3.03 (2.34 to 3.72) | 56.2 | within_limits | - |
| T-DRY-127 School Rd pole | Town of Dryden (DRY) | 50.0 kVA | 33.4 | stable | 4.12 (3.18 to 5.06) | 36.3 | within_limits | - |
| T-DRY-128 Hollow Rd pole | Town of Dryden (DRY) | 50.0 kVA | 31.5 | stable | 3.35 (2.58 to 4.11) | 35.5 | within_limits | - |
| T-DRY-129 Cemetery Rd pad | Town of Dryden (DRY) | 250.0 kVA | 205.0 | signal | not calculated | - | inspect_now | - |
| T-DRY-130 Main St pole | Town of Dryden (DRY) | 75.0 kVA | 48.3 | stable | 3.64 (2.81 to 4.47) | 53.6 | within_limits | - |
| T-DRY-131 Cemetery Rd pole | Town of Dryden (DRY) | 75.0 kVA | 52.3 | signal | not calculated | - | review_needed | - |
| T-DRY-132 Creek Rd pole | Town of Dryden (DRY) | 75.0 kVA | 45.6 | stable | 3.27 (2.52 to 4.02) | 50.4 | within_limits | - |
| T-DRY-133 School Rd pad | Town of Dryden (DRY) | 100.0 kVA | 61.8 | stable | 3.64 (2.81 to 4.47) | 67.8 | within_limits | - |
| T-DRY-134 Creek Rd pad | Town of Dryden (DRY) | 250.0 kVA | 170.6 | stable | 2.84 (2.19 to 3.49) | 194.3 | within_limits | - |
| T-DRY-135 Lake Rd pad | Town of Dryden (DRY) | 167.0 kVA | 120.2 | signal | not calculated | - | inspect_now | - |
| T-DRY-136 Mill St pole | Town of Dryden (DRY) | 75.0 kVA | 46.9 | stable | 3.60 (2.78 to 4.42) | 54.0 | within_limits | - |
| T-DRY-137 Orchard Rd pole | Town of Dryden (DRY) | 75.0 kVA | 53.3 | stable | 3.35 (2.58 to 4.12) | 59.4 | within_limits | - |
| T-DRY-138 Brook Rd pad | Town of Dryden (DRY) | 100.0 kVA | 64.9 | stable | 3.50 (2.70 to 4.30) | 73.4 | within_limits | - |
| T-DRY-139 Station Rd pad | Town of Dryden (DRY) | 167.0 kVA | 106.3 | stable | 3.30 (2.54 to 4.05) | 122.4 | within_limits | - |
| T-DRY-140 Cemetery Rd pole | Town of Dryden (DRY) | 50.0 kVA | 31.3 | stable | 3.55 (2.74 to 4.37) | 34.6 | within_limits | - |
| T-DRY-141 Forest Home Dr pad | Town of Dryden (DRY) | 100.0 kVA | 70.4 | signal | not calculated | - | inspect_now | - |
| T-DRY-142 Station Rd pole | Town of Dryden (DRY) | 75.0 kVA | 46.8 | stable | 3.20 (2.47 to 3.94) | 51.1 | within_limits | - |
| T-DRY-143 Pine Tree Rd pad | Town of Dryden (DRY) | 333.0 kVA | 215.5 | stable | 3.26 (2.51 to 4.00) | 240.3 | within_limits | - |
| T-DRY-144 Pine Tree Rd pole | Town of Dryden (DRY) | 75.0 kVA | 49.9 | stable | 3.06 (2.36 to 3.76) | 56.8 | within_limits | - |
| T-DRY-145 Creek Rd pole | Town of Dryden (DRY) | 75.0 kVA | 61.5 | signal | not calculated | - | review_needed | - |
| T-DRY-146 Pine Tree Rd pad | Town of Dryden (DRY) | 100.0 kVA | 64.9 | stable | 3.83 (2.96 to 4.71) | 70.8 | within_limits | - |
| T-DRY-147 Creek Rd pole | Town of Dryden (DRY) | 50.0 kVA | 31.1 | stable | 2.97 (2.29 to 3.65) | 35.5 | within_limits | - |
| T-ENF-011 Mecklenburg Rd pole | Town of Enfield (ENF) | 75.0 kVA | 78.7 | signal | not calculated | - | inspect_now | - |
| T-ENF-101 Falls Rd pad | Town of Enfield (ENF) | 100.0 kVA | 82.0 | signal | not calculated | - | review_needed | - |
| T-ENF-102 Falls Rd pad | Town of Enfield (ENF) | 100.0 kVA | 65.0 | stable | 3.34 (2.57 to 4.10) | 71.7 | within_limits | - |
| T-ENF-103 School Rd pole | Town of Enfield (ENF) | 50.0 kVA | 30.7 | insufficient_history | not calculated | - | review_needed | - |
| T-ENF-104 Church St pad | Town of Enfield (ENF) | 167.0 kVA | 99.5 | stable | 2.94 (2.27 to 3.62) | 114.7 | within_limits | - |
| T-ENF-105 Falls Rd pole | Town of Enfield (ENF) | 75.0 kVA | 51.6 | stable | 3.83 (2.95 to 4.70) | 56.0 | within_limits | - |
| T-ENF-106 Pine Tree Rd pole | Town of Enfield (ENF) | 75.0 kVA | 48.3 | stable | 3.54 (2.73 to 4.35) | 54.2 | within_limits | - |
| T-ENF-107 School Rd pad | Town of Enfield (ENF) | 333.0 kVA | 348.6 | signal | not calculated | - | inspect_now | - |
| T-ENF-108 School Rd pad | Town of Enfield (ENF) | 100.0 kVA | 65.1 | stable | 2.83 (2.18 to 3.47) | 71.7 | within_limits | - |
| T-ENF-109 Falls Rd pole | Town of Enfield (ENF) | 75.0 kVA | 48.5 | stable | 3.37 (2.60 to 4.15) | 53.2 | within_limits | - |
| T-ENF-110 Brook Rd pole | Town of Enfield (ENF) | 25.0 kVA | 15.3 | stable | 3.65 (2.82 to 4.49) | 16.8 | within_limits | - |
| T-ENF-111 Forest Home Dr pole | Town of Enfield (ENF) | 37.5 kVA | 24.0 | stable | 2.85 (2.20 to 3.50) | 26.4 | within_limits | - |
| T-ENF-112 Falls Rd pole | Town of Enfield (ENF) | 37.5 kVA | 28.1 | stable | 1.62 (1.24 to 1.99) | 31.1 | review_needed | - |
| T-ENF-113 Falls Rd pole | Town of Enfield (ENF) | 75.0 kVA | 49.5 | stable | 3.31 (2.55 to 4.07) | 54.4 | within_limits | - |
| T-ENF-114 Valley Rd pad | Town of Enfield (ENF) | 100.0 kVA | 66.2 | stable | 3.02 (2.33 to 3.71) | 73.1 | within_limits | - |
| T-ENF-115 Orchard Rd pole | Town of Enfield (ENF) | 50.0 kVA | 33.2 | stable | 3.11 (2.40 to 3.82) | 38.0 | within_limits | - |
| T-ENF-116 Hill Rd pole | Town of Enfield (ENF) | 50.0 kVA | 30.9 | stable | 2.92 (2.25 to 3.59) | 34.4 | within_limits | - |
| T-ENF-117 Falls Rd pad | Town of Enfield (ENF) | 250.0 kVA | 155.9 | stable | 3.37 (2.60 to 4.13) | 170.4 | within_limits | - |
| T-ENF-118 Ridge Rd pad | Town of Enfield (ENF) | 100.0 kVA | 64.7 | stable | 2.75 (2.12 to 3.38) | 73.0 | within_limits | - |
| T-ENF-119 Ridge Rd pole | Town of Enfield (ENF) | 75.0 kVA | 49.1 | stable | 3.38 (2.61 to 4.16) | 54.8 | within_limits | - |
| T-ENF-120 Pine Tree Rd pad | Town of Enfield (ENF) | 333.0 kVA | 232.3 | stable | 3.15 (2.43 to 3.87) | 254.7 | within_limits | - |
| T-ENF-121 Lake Rd pad | Town of Enfield (ENF) | 250.0 kVA | 163.5 | stable | 3.10 (2.39 to 3.81) | 184.1 | within_limits | - |
| T-ENF-122 Cemetery Rd pad | Town of Enfield (ENF) | 167.0 kVA | 105.8 | stable | 3.16 (2.44 to 3.88) | 121.8 | within_limits | - |
| T-ENF-123 Maple Ave pad | Town of Enfield (ENF) | 250.0 kVA | 156.3 | stable | 3.04 (2.34 to 3.73) | 171.9 | within_limits | - |
| T-ENF-124 Forest Home Dr pad | Town of Enfield (ENF) | 100.0 kVA | 64.5 | stable | 2.82 (2.18 to 3.47) | 70.6 | within_limits | - |
| T-ENF-125 Forest Home Dr pole | Town of Enfield (ENF) | 75.0 kVA | 52.3 | stable | 3.35 (2.58 to 4.12) | 56.8 | within_limits | - |
| T-ENF-126 Pine Tree Rd pole | Town of Enfield (ENF) | 50.0 kVA | 32.5 | stable | 2.95 (2.27 to 3.62) | 37.2 | within_limits | - |
| T-ENF-127 Pine Tree Rd pole | Town of Enfield (ENF) | 75.0 kVA | 48.5 | stable | 3.58 (2.77 to 4.40) | 52.9 | within_limits | - |
| T-ENF-128 Hill Rd pole | Town of Enfield (ENF) | 50.0 kVA | 31.9 | stable | 2.95 (2.28 to 3.63) | 35.3 | within_limits | - |
| T-ENF-129 Lake Rd pole | Town of Enfield (ENF) | 50.0 kVA | 32.0 | stable | 2.82 (2.18 to 3.47) | 36.6 | within_limits | - |
| T-ENF-130 Ridge Rd pole | Town of Enfield (ENF) | 37.5 kVA | 23.9 | stable | 2.96 (2.29 to 3.64) | 26.3 | within_limits | - |
| T-GRO-009 Peruville Rd pad | Town of Groton (GRO) | 100.0 kVA | 71.5 | signal | not calculated | - | inspect_now | - |
| T-GRO-101 Pine Tree Rd pole | Town of Groton (GRO) | 25.0 kVA | 16.4 | stable | 3.36 (2.59 to 4.13) | 18.0 | within_limits | - |
| T-GRO-102 Pine Tree Rd pad | Town of Groton (GRO) | 100.0 kVA | 63.4 | stable | 2.95 (2.27 to 3.63) | 70.3 | within_limits | - |
| T-GRO-103 Lake Rd pole | Town of Groton (GRO) | 75.0 kVA | 47.8 | stable | 4.29 (3.31 to 5.26) | 53.3 | within_limits | - |
| T-GRO-104 Falls Rd pad | Town of Groton (GRO) | 100.0 kVA | 64.7 | stable | 3.94 (3.04 to 4.83) | 72.0 | within_limits | - |
| T-GRO-105 Hollow Rd pole | Town of Groton (GRO) | 37.5 kVA | 24.4 | stable | 3.40 (2.62 to 4.18) | 27.2 | within_limits | - |
| T-GRO-106 Hill Rd pole | Town of Groton (GRO) | 37.5 kVA | 30.8 | signal | not calculated | - | review_needed | - |
| T-GRO-107 Forest Home Dr pole | Town of Groton (GRO) | 50.0 kVA | 31.1 | stable | 3.64 (2.80 to 4.47) | 36.0 | within_limits | - |
| T-GRO-108 Falls Rd pole | Town of Groton (GRO) | 50.0 kVA | 31.0 | stable | 3.45 (2.66 to 4.23) | 35.0 | within_limits | - |
| T-GRO-109 Falls Rd pole | Town of Groton (GRO) | 75.0 kVA | 47.5 | stable | 3.54 (2.73 to 4.34) | 53.4 | within_limits | - |
| T-GRO-110 Hollow Rd pole | Town of Groton (GRO) | 37.5 kVA | 23.8 | stable | 2.81 (2.17 to 3.45) | 27.1 | within_limits | - |
| T-GRO-111 Falls Rd pad | Town of Groton (GRO) | 167.0 kVA | 102.0 | stable | 3.73 (2.88 to 4.58) | 115.2 | within_limits | - |
| T-GRO-112 Creek Rd pad | Town of Groton (GRO) | 100.0 kVA | 68.5 | stable | 2.79 (2.15 to 3.43) | 75.7 | within_limits | - |
| T-GRO-113 Elm St pole | Town of Groton (GRO) | 50.0 kVA | 30.7 | stable | 3.19 (2.46 to 3.93) | 34.0 | within_limits | - |
| T-GRO-114 Station Rd pole | Town of Groton (GRO) | 75.0 kVA | 61.5 | signal | not calculated | - | review_needed | - |
| T-GRO-115 Station Rd pad | Town of Groton (GRO) | 333.0 kVA | 215.7 | stable | 4.25 (3.28 to 5.22) | 246.4 | within_limits | - |
| T-GRO-116 Pine Tree Rd pad | Town of Groton (GRO) | 100.0 kVA | 62.6 | stable | 3.13 (2.41 to 3.84) | 69.2 | within_limits | - |
| T-GRO-117 Brook Rd pole | Town of Groton (GRO) | 50.0 kVA | 33.1 | stable | 3.29 (2.54 to 4.05) | 37.1 | within_limits | - |
| T-GRO-118 Main St pole | Town of Groton (GRO) | 75.0 kVA | 77.2 | signal | not calculated | - | inspect_now | - |
| T-GRO-119 Forest Home Dr pole | Town of Groton (GRO) | 75.0 kVA | 48.1 | stable | 3.10 (2.39 to 3.80) | 52.6 | within_limits | - |
| T-GRO-120 Creek Rd pole | Town of Groton (GRO) | 75.0 kVA | 48.7 | stable | 2.87 (2.21 to 3.52) | 54.9 | within_limits | - |
| T-GRO-121 Valley Rd pad | Town of Groton (GRO) | 167.0 kVA | 109.4 | stable | 2.95 (2.27 to 3.62) | 119.9 | within_limits | - |
| T-GRO-122 Hollow Rd pad | Town of Groton (GRO) | 250.0 kVA | 165.9 | stable | 3.72 (2.87 to 4.57) | 189.2 | within_limits | - |
| T-GRO-123 School Rd pad | Town of Groton (GRO) | 100.0 kVA | 66.9 | stable | 4.04 (3.12 to 4.96) | 72.9 | within_limits | - |
| T-GRO-124 Lake Rd pole | Town of Groton (GRO) | 75.0 kVA | 45.9 | stable | 2.78 (2.14 to 3.42) | 51.9 | within_limits | - |
| T-GRO-125 Lake Rd pole | Town of Groton (GRO) | 75.0 kVA | 46.7 | stable | 3.42 (2.64 to 4.20) | 53.8 | within_limits | - |
| T-GRO-126 Creek Rd pad | Town of Groton (GRO) | 167.0 kVA | 111.5 | stable | 3.46 (2.67 to 4.25) | 125.0 | within_limits | - |
| T-GRO-127 Cemetery Rd pole | Town of Groton (GRO) | 75.0 kVA | 48.7 | stable | 3.09 (2.39 to 3.80) | 54.9 | within_limits | - |
| T-GRO-128 Orchard Rd pad | Town of Groton (GRO) | 167.0 kVA | 107.2 | stable | 3.24 (2.50 to 3.98) | 117.3 | within_limits | - |
| T-GRO-129 Main St pad | Town of Groton (GRO) | 100.0 kVA | 64.3 | stable | 3.39 (2.62 to 4.16) | 74.3 | within_limits | - |
| T-GRO-130 Ridge Rd pad | Town of Groton (GRO) | 100.0 kVA | 66.8 | stable | 3.08 (2.37 to 3.78) | 73.1 | within_limits | - |
| T-GRO-131 Creek Rd pole | Town of Groton (GRO) | 50.0 kVA | 34.4 | stable | 2.96 (2.29 to 3.64) | 37.6 | within_limits | - |
| T-GRO-132 Station Rd pad | Town of Groton (GRO) | 500.0 kVA | 323.2 | stable | 3.75 (2.90 to 4.61) | 353.9 | within_limits | - |
| T-GRO-133 Forest Home Dr pad | Town of Groton (GRO) | 100.0 kVA | 66.0 | stable | 2.87 (2.21 to 3.52) | 71.9 | within_limits | - |
| T-GRO-134 Main St pad | Town of Groton (GRO) | 100.0 kVA | 70.8 | stable | 2.78 (2.14 to 3.42) | 80.1 | within_limits | - |
| T-GRO-135 Mill St pad | Town of Groton (GRO) | 333.0 kVA | 275.6 | stable | 1.05 (0.80 to 1.31) | 298.2 | review_needed | - |
| T-GRO-136 Main St pad | Town of Groton (GRO) | 167.0 kVA | 110.0 | stable | 3.45 (2.66 to 4.24) | 123.9 | within_limits | - |
| T-GRO-137 Forest Home Dr pole | Town of Groton (GRO) | 50.0 kVA | 32.6 | stable | 3.49 (2.69 to 4.28) | 36.6 | within_limits | - |
| T-ITC-101 Forest Home Dr pole | City of Ithaca (ITH-C) | 75.0 kVA | 48.5 | stable | 3.40 (2.62 to 4.17) | 53.9 | within_limits | - |
| T-ITC-102 Forest Home Dr pole | City of Ithaca (ITH-C) | 50.0 kVA | 42.5 | stable | 1.11 (0.85 to 1.38) | 46.3 | review_needed | - |
| T-ITC-103 Falls Rd pole | City of Ithaca (ITH-C) | 25.0 kVA | 16.5 | stable | 3.04 (2.34 to 3.73) | 18.1 | within_limits | - |
| T-ITC-104 Pine Tree Rd pad | City of Ithaca (ITH-C) | 167.0 kVA | 122.0 | signal | not calculated | - | inspect_now | - |
| T-ITC-105 Cemetery Rd pole | City of Ithaca (ITH-C) | 37.5 kVA | 25.9 | stable | 3.27 (2.52 to 4.02) | 29.2 | within_limits | - |
| T-ITC-106 Station Rd pole | City of Ithaca (ITH-C) | 25.0 kVA | 18.0 | stable | 1.48 (1.14 to 1.83) | 19.7 | review_needed | - |
| T-ITC-107 Hanshaw Rd pad | City of Ithaca (ITH-C) | 100.0 kVA | 69.7 | stable | 2.94 (2.26 to 3.61) | 76.3 | within_limits | - |
| T-ITC-108 Station Rd pad | City of Ithaca (ITH-C) | 250.0 kVA | 160.6 | stable | 3.37 (2.60 to 4.15) | 178.6 | within_limits | - |
| T-ITC-109 Hanshaw Rd pad | City of Ithaca (ITH-C) | 250.0 kVA | 154.4 | stable | 3.47 (2.68 to 4.27) | 169.1 | within_limits | - |
| T-ITC-110 Hanshaw Rd pole | City of Ithaca (ITH-C) | 75.0 kVA | 50.8 | stable | 3.01 (2.32 to 3.69) | 55.6 | within_limits | - |
| T-ITC-111 Hollow Rd pad | City of Ithaca (ITH-C) | 333.0 kVA | 232.7 | stable | 2.76 (2.13 to 3.40) | 259.1 | within_limits | - |
| T-ITC-112 Creek Rd pole | City of Ithaca (ITH-C) | 75.0 kVA | 47.7 | stable | 2.70 (2.08 to 3.32) | 53.1 | within_limits | - |
| T-ITC-113 Pine Tree Rd pad | City of Ithaca (ITH-C) | 100.0 kVA | 63.4 | stable | 3.12 (2.40 to 3.83) | 70.1 | within_limits | - |
| T-ITC-114 Brook Rd pad | City of Ithaca (ITH-C) | 250.0 kVA | 211.2 | stable | 1.11 (0.84 to 1.37) | 230.2 | review_needed | - |
| T-ITC-115 Elm St pad | City of Ithaca (ITH-C) | 250.0 kVA | 183.3 | stable | 2.27 (1.74 to 2.79) | 201.1 | within_limits | - |
| T-ITC-116 Valley Rd pole | City of Ithaca (ITH-C) | 75.0 kVA | 46.9 | stable | 3.64 (2.80 to 4.47) | 54.0 | within_limits | - |
| T-ITC-117 Valley Rd pole | City of Ithaca (ITH-C) | 50.0 kVA | 31.8 | stable | 3.21 (2.47 to 3.94) | 35.1 | within_limits | - |
| T-ITC-118 Creek Rd pole | City of Ithaca (ITH-C) | 37.5 kVA | 24.6 | stable | 2.75 (2.12 to 3.38) | 26.9 | within_limits | - |
| T-ITC-119 Falls Rd pad | City of Ithaca (ITH-C) | 167.0 kVA | 105.8 | stable | 2.94 (2.27 to 3.62) | 115.7 | within_limits | - |
| T-ITC-120 Brook Rd pole | City of Ithaca (ITH-C) | 75.0 kVA | 50.3 | stable | 3.47 (2.67 to 4.26) | 55.0 | within_limits | - |
| T-ITC-121 Ridge Rd pole | City of Ithaca (ITH-C) | 75.0 kVA | 48.1 | stable | 2.96 (2.28 to 3.64) | 52.5 | within_limits | - |
| T-ITC-122 Station Rd pole | City of Ithaca (ITH-C) | 50.0 kVA | 41.0 | signal | not calculated | - | review_needed | - |
| T-ITC-123 School Rd pole | City of Ithaca (ITH-C) | 25.0 kVA | 15.7 | stable | 3.72 (2.87 to 4.57) | 18.1 | within_limits | - |
| T-ITC-124 Valley Rd pole | City of Ithaca (ITH-C) | 50.0 kVA | 37.3 | stable | 1.34 (1.02 to 1.66) | 41.2 | review_needed | - |
| T-ITC-125 Cemetery Rd pole | City of Ithaca (ITH-C) | 75.0 kVA | 48.7 | stable | 2.72 (2.10 to 3.35) | 53.2 | within_limits | - |
| T-ITC-126 Hollow Rd pole | City of Ithaca (ITH-C) | 75.0 kVA | 48.7 | stable | 3.27 (2.52 to 4.01) | 54.0 | within_limits | - |
| T-ITC-127 Hanshaw Rd pad | City of Ithaca (ITH-C) | 100.0 kVA | 82.0 | signal | not calculated | - | review_needed | - |
| T-ITC-128 Maple Ave pad | City of Ithaca (ITH-C) | 100.0 kVA | 90.1 | stable | 0.92 (0.69 to 1.14) | 100.0 | review_needed | - |
| T-ITC-129 Ridge Rd pole | City of Ithaca (ITH-C) | 50.0 kVA | 34.6 | stable | 3.13 (2.41 to 3.85) | 38.6 | within_limits | - |
| T-ITC-130 Valley Rd pole | City of Ithaca (ITH-C) | 75.0 kVA | 50.0 | stable | 3.49 (2.69 to 4.28) | 56.0 | within_limits | - |
| T-ITC-131 Ridge Rd pole | City of Ithaca (ITH-C) | 75.0 kVA | 47.0 | stable | 3.88 (2.99 to 4.76) | 51.6 | within_limits | - |
| T-ITC-132 Orchard Rd pole | City of Ithaca (ITH-C) | 75.0 kVA | 49.8 | stable | 2.99 (2.31 to 3.68) | 56.2 | within_limits | - |
| T-ITC-133 Maple Ave pad | City of Ithaca (ITH-C) | 333.0 kVA | 267.0 | stable | 1.68 (1.29 to 2.07) | 298.1 | review_needed | - |
| T-ITC-134 Elm St pole | City of Ithaca (ITH-C) | 50.0 kVA | 43.8 | stable | 0.87 (0.66 to 1.09) | 46.9 | review_needed | - |
| T-ITC-135 Creek Rd pad | City of Ithaca (ITH-C) | 100.0 kVA | 104.8 | signal | not calculated | - | inspect_now | - |
| T-ITC-136 Hill Rd pole | City of Ithaca (ITH-C) | 25.0 kVA | 17.2 | stable | 3.19 (2.46 to 3.92) | 19.4 | within_limits | - |
| T-ITC-137 Creek Rd pole | City of Ithaca (ITH-C) | 50.0 kVA | 31.5 | stable | 2.70 (2.08 to 3.32) | 36.4 | within_limits | - |
| T-ITC-138 Forest Home Dr pole | City of Ithaca (ITH-C) | 37.5 kVA | 25.2 | stable | 2.72 (2.09 to 3.34) | 28.8 | within_limits | - |
| T-ITC-139 Brook Rd pole | City of Ithaca (ITH-C) | 25.0 kVA | 20.8 | stable | 1.48 (1.13 to 1.83) | 22.4 | review_needed | - |
| T-ITC-140 Maple Ave pole | City of Ithaca (ITH-C) | 75.0 kVA | 47.1 | insufficient_history | not calculated | - | review_needed | - |
| T-ITC-141 Maple Ave pole | City of Ithaca (ITH-C) | 37.5 kVA | 25.0 | stable | 3.07 (2.37 to 3.78) | 27.3 | within_limits | - |
| T-ITC-142 Ridge Rd pad | City of Ithaca (ITH-C) | 167.0 kVA | 111.8 | stable | 3.47 (2.68 to 4.26) | 122.6 | within_limits | - |
| T-ITC-143 Falls Rd pad | City of Ithaca (ITH-C) | 100.0 kVA | 60.7 | stable | 3.56 (2.75 to 4.38) | 66.6 | within_limits | - |
| T-ITC-144 Hollow Rd pole | City of Ithaca (ITH-C) | 50.0 kVA | 33.8 | stable | 3.15 (2.43 to 3.87) | 37.7 | within_limits | - |
| T-ITC-145 Hill Rd pole | City of Ithaca (ITH-C) | 50.0 kVA | 41.0 | signal | not calculated | - | review_needed | - |
| T-ITC-146 Lake Rd pole | City of Ithaca (ITH-C) | 75.0 kVA | 47.0 | stable | 3.61 (2.79 to 4.44) | 52.9 | within_limits | - |
| T-ITC-147 Cemetery Rd pad | City of Ithaca (ITH-C) | 250.0 kVA | 205.0 | signal | not calculated | - | review_needed | - |
| T-ITC-148 Lake Rd pole | City of Ithaca (ITH-C) | 50.0 kVA | 31.4 | stable | 3.02 (2.33 to 3.71) | 34.2 | within_limits | - |
| T-ITC-149 Brook Rd pad | City of Ithaca (ITH-C) | 333.0 kVA | 205.0 | stable | 3.79 (2.93 to 4.66) | 228.3 | within_limits | - |
| T-ITC-150 Orchard Rd pole | City of Ithaca (ITH-C) | 75.0 kVA | 79.5 | signal | not calculated | - | inspect_now | - |
| T-ITC-151 School Rd pad | City of Ithaca (ITH-C) | 100.0 kVA | 70.8 | stable | 2.74 (2.11 to 3.37) | 78.5 | within_limits | - |
| T-ITC-152 Creek Rd pad | City of Ithaca (ITH-C) | 100.0 kVA | 63.8 | stable | 3.44 (2.65 to 4.22) | 72.9 | within_limits | - |
| T-ITC-153 Hill Rd pole | City of Ithaca (ITH-C) | 75.0 kVA | 50.4 | stable | 2.76 (2.13 to 3.39) | 56.7 | within_limits | - |
| T-ITC-154 Cemetery Rd pole | City of Ithaca (ITH-C) | 25.0 kVA | 16.4 | stable | 3.15 (2.43 to 3.87) | 18.2 | within_limits | - |
| T-ITC-155 Valley Rd pad | City of Ithaca (ITH-C) | 100.0 kVA | 63.8 | stable | 3.11 (2.40 to 3.82) | 73.7 | within_limits | - |
| T-ITC-156 Hollow Rd pole | City of Ithaca (ITH-C) | 50.0 kVA | 34.4 | stable | 2.92 (2.25 to 3.59) | 37.3 | within_limits | - |
| T-ITC-157 Valley Rd pole | City of Ithaca (ITH-C) | 50.0 kVA | 31.8 | stable | 2.96 (2.28 to 3.63) | 35.5 | within_limits | - |
| T-ITC-158 Main St pole | City of Ithaca (ITH-C) | 75.0 kVA | 48.1 | stable | 3.55 (2.74 to 4.36) | 52.8 | within_limits | - |
| T-ITC-159 Valley Rd pad | City of Ithaca (ITH-C) | 167.0 kVA | 145.9 | stable | 1.00 (0.76 to 1.24) | 156.3 | review_needed | - |
| T-ITC-160 Hanshaw Rd pole | City of Ithaca (ITH-C) | 75.0 kVA | 50.1 | stable | 3.15 (2.43 to 3.87) | 54.4 | within_limits | - |
| T-ITC-161 Station Rd pole | City of Ithaca (ITH-C) | 75.0 kVA | 49.4 | stable | 3.11 (2.40 to 3.82) | 54.2 | within_limits | - |
| T-ITC-162 Forest Home Dr pole | City of Ithaca (ITH-C) | 50.0 kVA | 33.4 | stable | 3.50 (2.70 to 4.31) | 37.0 | within_limits | - |
| T-ITC-163 Valley Rd pad | City of Ithaca (ITH-C) | 167.0 kVA | 103.4 | stable | 3.46 (2.67 to 4.25) | 118.5 | within_limits | - |
| T-ITC-164 School Rd pole | City of Ithaca (ITH-C) | 50.0 kVA | 31.9 | stable | 3.26 (2.51 to 4.00) | 36.0 | within_limits | - |
| T-ITC-165 Orchard Rd pole | City of Ithaca (ITH-C) | 50.0 kVA | 31.3 | stable | 2.98 (2.29 to 3.66) | 34.3 | within_limits | - |
| T-ITC-166 Pine Tree Rd pole | City of Ithaca (ITH-C) | 50.0 kVA | 32.7 | stable | 3.61 (2.79 to 4.44) | 37.0 | within_limits | - |
| T-ITC-167 Station Rd pad | City of Ithaca (ITH-C) | 167.0 kVA | 109.5 | stable | 2.64 (2.04 to 3.25) | 119.8 | within_limits | - |
| T-ITC-168 Ridge Rd pole | City of Ithaca (ITH-C) | 50.0 kVA | 32.2 | stable | 3.33 (2.57 to 4.09) | 36.1 | within_limits | - |
| T-ITC-169 Brook Rd pole | City of Ithaca (ITH-C) | 75.0 kVA | 47.9 | stable | 3.70 (2.85 to 4.54) | 52.1 | within_limits | - |
| T-ITC-170 Church St pad | City of Ithaca (ITH-C) | 167.0 kVA | 108.5 | stable | 2.93 (2.26 to 3.61) | 118.2 | within_limits | - |
| T-ITC-171 Valley Rd pad | City of Ithaca (ITH-C) | 250.0 kVA | 167.1 | stable | 3.30 (2.55 to 4.06) | 187.9 | within_limits | - |
| T-ITC-172 Church St pole | City of Ithaca (ITH-C) | 50.0 kVA | 32.5 | stable | 3.42 (2.64 to 4.20) | 36.2 | within_limits | - |
| T-ITC-173 Hill Rd pole | City of Ithaca (ITH-C) | 50.0 kVA | 41.0 | signal | not calculated | - | review_needed | - |
| T-ITC-174 Hanshaw Rd pad | City of Ithaca (ITH-C) | 167.0 kVA | 103.3 | stable | 2.84 (2.19 to 3.50) | 115.0 | within_limits | - |
| T-ITC-175 Lake Rd pad | City of Ithaca (ITH-C) | 100.0 kVA | 63.5 | stable | 3.01 (2.32 to 3.71) | 72.2 | within_limits | - |
| T-ITC-176 Main St pole | City of Ithaca (ITH-C) | 75.0 kVA | 49.1 | stable | 2.74 (2.11 to 3.37) | 53.7 | within_limits | - |
| T-ITC-177 Elm St pole | City of Ithaca (ITH-C) | 25.0 kVA | 15.8 | stable | 3.21 (2.48 to 3.95) | 17.6 | within_limits | - |
| T-ITC-178 Cemetery Rd pad | City of Ithaca (ITH-C) | 167.0 kVA | 106.2 | stable | 4.22 (3.26 to 5.18) | 122.6 | within_limits | - |
| T-ITC-179 Hill Rd pole | City of Ithaca (ITH-C) | 50.0 kVA | 33.8 | stable | 2.81 (2.16 to 3.45) | 36.9 | within_limits | - |
| T-ITC-180 Mill St pole | City of Ithaca (ITH-C) | 75.0 kVA | 48.1 | stable | 3.55 (2.74 to 4.37) | 52.7 | within_limits | - |
| T-ITC-181 Cemetery Rd pole | City of Ithaca (ITH-C) | 50.0 kVA | 33.0 | stable | 3.15 (2.43 to 3.87) | 36.6 | within_limits | - |
| T-ITC-182 Forest Home Dr pad | City of Ithaca (ITH-C) | 167.0 kVA | 113.6 | stable | 3.11 (2.40 to 3.82) | 127.9 | within_limits | - |
| T-ITC-183 Mill St pole | City of Ithaca (ITH-C) | 50.0 kVA | 43.6 | stable | 1.02 (0.77 to 1.27) | 46.8 | review_needed | - |
| T-ITC-184 Main St pad | City of Ithaca (ITH-C) | 167.0 kVA | 109.2 | stable | 4.00 (3.09 to 4.92) | 119.1 | within_limits | - |
| T-ITC-185 Forest Home Dr pole | City of Ithaca (ITH-C) | 50.0 kVA | 34.4 | stable | 3.09 (2.39 to 3.80) | 38.2 | within_limits | - |
| T-ITC-186 School Rd pad | City of Ithaca (ITH-C) | 167.0 kVA | 101.1 | stable | 3.70 (2.86 to 4.55) | 115.5 | within_limits | - |
| T-ITC-187 Main St pad | City of Ithaca (ITH-C) | 100.0 kVA | 64.8 | stable | 3.44 (2.65 to 4.22) | 74.7 | within_limits | - |
| T-ITC-188 Valley Rd pad | City of Ithaca (ITH-C) | 167.0 kVA | 106.7 | stable | 4.13 (3.19 to 5.08) | 116.6 | within_limits | - |
| T-ITC-189 Hanshaw Rd pole | City of Ithaca (ITH-C) | 50.0 kVA | 32.7 | stable | 2.85 (2.19 to 3.50) | 36.4 | within_limits | - |
| T-ITC-190 Forest Home Dr pad | City of Ithaca (ITH-C) | 100.0 kVA | 104.5 | signal | not calculated | - | inspect_now | - |
| T-ITC-191 Hill Rd pole | City of Ithaca (ITH-C) | 75.0 kVA | 48.8 | stable | 2.90 (2.24 to 3.57) | 53.4 | within_limits | - |
| T-ITC-192 Elm St pad | City of Ithaca (ITH-C) | 250.0 kVA | 186.5 | stable | 1.46 (1.12 to 1.80) | 201.8 | review_needed | - |
| T-ITC-193 Cemetery Rd pole | City of Ithaca (ITH-C) | 50.0 kVA | 43.9 | stable | 1.30 (1.00 to 1.61) | 46.7 | review_needed | - |
| T-ITC-194 Mill St pad | City of Ithaca (ITH-C) | 333.0 kVA | 351.4 | signal | not calculated | - | inspect_now | - |
| T-ITC-195 Valley Rd pole | City of Ithaca (ITH-C) | 75.0 kVA | 47.7 | stable | 3.07 (2.37 to 3.77) | 54.4 | within_limits | - |
| T-ITC-196 Maple Ave pole | City of Ithaca (ITH-C) | 50.0 kVA | 31.4 | stable | 3.39 (2.61 to 4.16) | 34.6 | within_limits | - |
| T-ITC-197 Hill Rd pad | City of Ithaca (ITH-C) | 100.0 kVA | 67.4 | stable | 2.93 (2.26 to 3.60) | 74.9 | within_limits | - |
| T-ITC-198 Brook Rd pad | City of Ithaca (ITH-C) | 100.0 kVA | 62.3 | insufficient_history | not calculated | - | review_needed | - |
| T-ITC-199 Forest Home Dr pad | City of Ithaca (ITH-C) | 167.0 kVA | 106.7 | stable | 2.72 (2.10 to 3.35) | 121.8 | within_limits | - |
| T-ITC-200 Cemetery Rd pad | City of Ithaca (ITH-C) | 100.0 kVA | 82.0 | signal | not calculated | - | review_needed | - |
| T-ITC-201 Hill Rd pole | City of Ithaca (ITH-C) | 75.0 kVA | 47.5 | stable | 2.90 (2.24 to 3.56) | 51.9 | within_limits | - |
| T-ITH-001 Stewart Ave pad | City of Ithaca (ITH-C) | 167.0 kVA | 108.8 | stable | 3.35 (2.58 to 4.11) | 123.0 | within_limits | - |
| T-ITH-002 Coddington Rd pole | Town of Ithaca (ITH-T) | 100.0 kVA | 63.2 | stable | 3.05 (2.35 to 3.75) | 71.3 | within_limits | - |
| T-ITT-101 Falls Rd pad | Town of Ithaca (ITH-T) | 100.0 kVA | 65.2 | stable | 3.13 (2.41 to 3.84) | 74.5 | within_limits | - |
| T-ITT-102 Elm St pole | Town of Ithaca (ITH-T) | 50.0 kVA | 32.3 | stable | 3.77 (2.91 to 4.63) | 36.1 | within_limits | - |
| T-ITT-103 Ridge Rd pad | Town of Ithaca (ITH-T) | 100.0 kVA | 60.7 | stable | 3.55 (2.74 to 4.36) | 66.3 | within_limits | - |
| T-ITT-104 Lake Rd pad | Town of Ithaca (ITH-T) | 250.0 kVA | 163.2 | stable | 3.13 (2.42 to 3.85) | 182.4 | within_limits | - |
| T-ITT-105 Church St pole | Town of Ithaca (ITH-T) | 50.0 kVA | 33.8 | stable | 3.19 (2.46 to 3.92) | 37.6 | within_limits | - |
| T-ITT-106 Hanshaw Rd pad | Town of Ithaca (ITH-T) | 100.0 kVA | 63.7 | stable | 3.17 (2.44 to 3.89) | 72.2 | within_limits | - |
| T-ITT-107 Creek Rd pad | Town of Ithaca (ITH-T) | 167.0 kVA | 108.6 | stable | 3.31 (2.55 to 4.06) | 118.9 | within_limits | - |
| T-ITT-108 Hanshaw Rd pole | Town of Ithaca (ITH-T) | 37.5 kVA | 28.7 | stable | 1.36 (1.04 to 1.68) | 30.9 | review_needed | - |
| T-ITT-109 Hollow Rd pole | Town of Ithaca (ITH-T) | 75.0 kVA | 49.3 | stable | 3.77 (2.91 to 4.63) | 55.0 | within_limits | - |
| T-ITT-110 Pine Tree Rd pad | Town of Ithaca (ITH-T) | 100.0 kVA | 70.1 | stable | 3.70 (2.86 to 4.55) | 76.6 | within_limits | - |
| T-ITT-111 Hollow Rd pad | Town of Ithaca (ITH-T) | 100.0 kVA | 64.3 | stable | 3.08 (2.38 to 3.79) | 70.4 | within_limits | - |
| T-ITT-112 Ridge Rd pole | Town of Ithaca (ITH-T) | 75.0 kVA | 49.3 | stable | 3.38 (2.61 to 4.15) | 55.3 | within_limits | - |
| T-ITT-113 Orchard Rd pole | Town of Ithaca (ITH-T) | 37.5 kVA | 32.9 | stable | 0.92 (0.69 to 1.14) | 35.3 | review_needed | - |
| T-ITT-114 Orchard Rd pad | Town of Ithaca (ITH-T) | 100.0 kVA | 63.4 | stable | 2.67 (2.06 to 3.29) | 70.7 | within_limits | - |
| T-ITT-115 Falls Rd pad | Town of Ithaca (ITH-T) | 167.0 kVA | 105.7 | stable | 3.11 (2.40 to 3.82) | 115.8 | within_limits | - |
| T-ITT-116 Church St pad | Town of Ithaca (ITH-T) | 167.0 kVA | 109.5 | stable | 3.28 (2.53 to 4.04) | 123.0 | within_limits | - |
| T-ITT-117 Orchard Rd pad | Town of Ithaca (ITH-T) | 100.0 kVA | 63.0 | stable | 2.89 (2.23 to 3.55) | 70.7 | within_limits | - |
| T-ITT-118 Cemetery Rd pad | Town of Ithaca (ITH-T) | 250.0 kVA | 169.0 | stable | 3.44 (2.65 to 4.22) | 192.8 | within_limits | - |
| T-ITT-119 Forest Home Dr pole | Town of Ithaca (ITH-T) | 25.0 kVA | 16.9 | stable | 3.16 (2.44 to 3.89) | 19.0 | within_limits | - |
| T-ITT-120 Forest Home Dr pole | Town of Ithaca (ITH-T) | 50.0 kVA | 45.6 | stable | 1.03 (0.78 to 1.28) | 49.7 | review_needed | - |
| T-ITT-121 Creek Rd pole | Town of Ithaca (ITH-T) | 25.0 kVA | 24.2 | stable | 1.08 (0.82 to 1.34) | 25.8 | review_needed | - |
| T-ITT-122 Hanshaw Rd pole | Town of Ithaca (ITH-T) | 37.5 kVA | 24.2 | stable | 3.25 (2.51 to 4.00) | 26.4 | within_limits | - |
| T-ITT-123 Maple Ave pad | Town of Ithaca (ITH-T) | 167.0 kVA | 105.3 | stable | 3.58 (2.76 to 4.39) | 121.1 | within_limits | - |
| T-ITT-124 Forest Home Dr pole | Town of Ithaca (ITH-T) | 75.0 kVA | 53.8 | signal | not calculated | - | inspect_now | - |
| T-ITT-125 Mill St pad | Town of Ithaca (ITH-T) | 167.0 kVA | 111.9 | stable | 3.44 (2.66 to 4.23) | 123.8 | within_limits | - |
| T-ITT-126 Hollow Rd pole | Town of Ithaca (ITH-T) | 50.0 kVA | 36.0 | stable | 2.91 (2.25 to 3.58) | 39.4 | within_limits | - |
| T-ITT-127 Church St pad | Town of Ithaca (ITH-T) | 167.0 kVA | 154.7 | stable | 1.21 (0.93 to 1.50) | 169.6 | review_needed | - |
| T-ITT-128 School Rd pole | Town of Ithaca (ITH-T) | 75.0 kVA | 61.5 | signal | not calculated | - | review_needed | - |
| T-ITT-129 Brook Rd pole | Town of Ithaca (ITH-T) | 50.0 kVA | 34.1 | stable | 3.13 (2.42 to 3.85) | 37.9 | within_limits | - |
| T-ITT-130 Hill Rd pole | Town of Ithaca (ITH-T) | 50.0 kVA | 41.0 | signal | not calculated | - | review_needed | - |
| T-ITT-131 Brook Rd pole | Town of Ithaca (ITH-T) | 50.0 kVA | 32.7 | stable | 3.31 (2.55 to 4.07) | 36.8 | within_limits | - |
| T-ITT-132 Elm St pole | Town of Ithaca (ITH-T) | 50.0 kVA | 32.3 | stable | 3.07 (2.37 to 3.77) | 35.5 | within_limits | - |
| T-ITT-133 Lake Rd pad | Town of Ithaca (ITH-T) | 500.0 kVA | 343.3 | stable | 3.22 (2.48 to 3.96) | 372.8 | within_limits | - |
| T-ITT-134 Pine Tree Rd pole | Town of Ithaca (ITH-T) | 50.0 kVA | 33.9 | stable | 3.34 (2.57 to 4.10) | 38.3 | within_limits | - |
| T-ITT-135 Elm St pole | Town of Ithaca (ITH-T) | 37.5 kVA | 24.1 | stable | 3.27 (2.52 to 4.01) | 27.1 | within_limits | - |
| T-ITT-136 Station Rd pad | Town of Ithaca (ITH-T) | 167.0 kVA | 116.4 | stable | 3.04 (2.35 to 3.74) | 127.3 | within_limits | - |
| T-ITT-137 Hollow Rd pole | Town of Ithaca (ITH-T) | 37.5 kVA | 30.8 | signal | not calculated | - | review_needed | - |
| T-ITT-138 Cemetery Rd pole | Town of Ithaca (ITH-T) | 75.0 kVA | 49.1 | stable | 3.06 (2.36 to 3.76) | 55.2 | within_limits | - |
| T-ITT-139 Orchard Rd pole | Town of Ithaca (ITH-T) | 75.0 kVA | 48.0 | stable | 3.29 (2.54 to 4.04) | 52.9 | within_limits | - |
| T-ITT-140 School Rd pole | Town of Ithaca (ITH-T) | 75.0 kVA | 48.9 | stable | 3.37 (2.60 to 4.15) | 56.1 | within_limits | - |
| T-ITT-141 Mill St pole | Town of Ithaca (ITH-T) | 50.0 kVA | 33.3 | stable | 3.57 (2.76 to 4.39) | 36.6 | within_limits | - |
| T-ITT-142 Pine Tree Rd pole | Town of Ithaca (ITH-T) | 25.0 kVA | 17.1 | stable | 3.08 (2.38 to 3.79) | 18.9 | within_limits | - |
| T-ITT-143 Hanshaw Rd pole | Town of Ithaca (ITH-T) | 50.0 kVA | 33.6 | stable | 3.00 (2.32 to 3.69) | 37.0 | within_limits | - |
| T-ITT-144 Forest Home Dr pole | Town of Ithaca (ITH-T) | 37.5 kVA | 25.1 | stable | 3.18 (2.46 to 3.91) | 27.4 | within_limits | - |
| T-ITT-145 Church St pole | Town of Ithaca (ITH-T) | 50.0 kVA | 31.4 | stable | 3.80 (2.93 to 4.67) | 36.0 | within_limits | - |
| T-ITT-146 Station Rd pole | Town of Ithaca (ITH-T) | 50.0 kVA | 34.1 | stable | 2.90 (2.23 to 3.56) | 38.8 | within_limits | - |
| T-ITT-147 Main St pole | Town of Ithaca (ITH-T) | 50.0 kVA | 33.2 | stable | 3.24 (2.50 to 3.99) | 37.4 | within_limits | - |
| T-ITT-148 Creek Rd pole | Town of Ithaca (ITH-T) | 37.5 kVA | 25.5 | stable | 2.96 (2.28 to 3.64) | 27.8 | within_limits | - |
| T-ITT-149 Forest Home Dr pole | Town of Ithaca (ITH-T) | 75.0 kVA | 50.3 | stable | 3.54 (2.73 to 4.35) | 55.4 | within_limits | - |
| T-ITT-150 Pine Tree Rd pad | Town of Ithaca (ITH-T) | 167.0 kVA | 110.5 | stable | 2.95 (2.28 to 3.63) | 123.6 | within_limits | - |
| T-ITT-151 Hill Rd pole | Town of Ithaca (ITH-T) | 50.0 kVA | 32.5 | stable | 3.17 (2.44 to 3.89) | 37.2 | within_limits | - |
| T-ITT-152 Cemetery Rd pad | Town of Ithaca (ITH-T) | 250.0 kVA | 159.3 | stable | 3.17 (2.44 to 3.89) | 181.1 | within_limits | - |
| T-ITT-153 Cemetery Rd pole | Town of Ithaca (ITH-T) | 50.0 kVA | 34.0 | stable | 3.13 (2.41 to 3.84) | 36.8 | within_limits | - |
| T-ITT-154 Hanshaw Rd pad | Town of Ithaca (ITH-T) | 100.0 kVA | 66.5 | stable | 3.01 (2.32 to 3.70) | 75.0 | within_limits | - |
| T-ITT-155 School Rd pole | Town of Ithaca (ITH-T) | 50.0 kVA | 33.4 | stable | 3.15 (2.43 to 3.86) | 37.8 | within_limits | - |
| T-ITT-156 Hollow Rd pad | Town of Ithaca (ITH-T) | 100.0 kVA | 67.1 | stable | 2.89 (2.22 to 3.55) | 73.0 | within_limits | - |
| T-ITT-157 Forest Home Dr pad | Town of Ithaca (ITH-T) | 167.0 kVA | 107.0 | stable | 3.18 (2.45 to 3.90) | 118.3 | within_limits | - |
| T-ITT-158 Valley Rd pad | Town of Ithaca (ITH-T) | 333.0 kVA | 235.1 | signal | not calculated | - | inspect_now | - |
| T-ITT-159 Valley Rd pad | Town of Ithaca (ITH-T) | 100.0 kVA | 64.2 | stable | 3.20 (2.47 to 3.94) | 71.1 | within_limits | - |
| T-ITT-160 Hanshaw Rd pad | Town of Ithaca (ITH-T) | 100.0 kVA | 82.0 | signal | not calculated | - | review_needed | - |
| T-ITT-161 Hanshaw Rd pad | Town of Ithaca (ITH-T) | 167.0 kVA | 136.9 | signal | not calculated | - | review_needed | - |
| T-ITT-162 Brook Rd pole | Town of Ithaca (ITH-T) | 50.0 kVA | 32.7 | stable | 3.17 (2.45 to 3.90) | 36.0 | within_limits | - |
| T-ITT-163 Pine Tree Rd pole | Town of Ithaca (ITH-T) | 75.0 kVA | 48.4 | stable | 2.90 (2.23 to 3.56) | 52.6 | within_limits | - |
| T-ITT-164 Creek Rd pad | Town of Ithaca (ITH-T) | 167.0 kVA | 105.3 | stable | 4.19 (3.23 to 5.14) | 115.4 | within_limits | - |
| T-ITT-165 Church St pole | Town of Ithaca (ITH-T) | 50.0 kVA | 45.6 | stable | 1.27 (0.97 to 1.57) | 48.7 | review_needed | - |
| T-ITT-166 Main St pad | Town of Ithaca (ITH-T) | 500.0 kVA | 317.9 | stable | 2.78 (2.14 to 3.41) | 347.0 | within_limits | - |
| T-ITT-167 Maple Ave pad | Town of Ithaca (ITH-T) | 100.0 kVA | 76.9 | stable | 1.52 (1.16 to 1.87) | 83.1 | review_needed | - |
| T-ITT-168 Orchard Rd pad | Town of Ithaca (ITH-T) | 250.0 kVA | 159.2 | stable | 3.29 (2.54 to 4.04) | 174.0 | within_limits | - |
| T-ITT-169 Elm St pole | Town of Ithaca (ITH-T) | 37.5 kVA | 24.9 | stable | 3.21 (2.47 to 3.94) | 27.0 | within_limits | - |
| T-ITT-170 Valley Rd pad | Town of Ithaca (ITH-T) | 100.0 kVA | 82.0 | signal | not calculated | - | review_needed | - |
| T-ITT-171 Falls Rd pad | Town of Ithaca (ITH-T) | 250.0 kVA | 166.8 | stable | 3.22 (2.49 to 3.96) | 186.0 | within_limits | - |
| T-ITT-172 Hill Rd pad | Town of Ithaca (ITH-T) | 167.0 kVA | 102.0 | stable | 3.51 (2.71 to 4.31) | 116.8 | within_limits | - |
| T-ITT-173 Falls Rd pole | Town of Ithaca (ITH-T) | 37.5 kVA | 23.7 | stable | 2.97 (2.29 to 3.65) | 27.3 | within_limits | - |
| T-ITT-174 Creek Rd pad | Town of Ithaca (ITH-T) | 167.0 kVA | 103.9 | stable | 3.25 (2.51 to 3.99) | 115.0 | within_limits | - |
| T-ITT-175 Station Rd pole | Town of Ithaca (ITH-T) | 75.0 kVA | 47.3 | stable | 3.16 (2.44 to 3.89) | 51.8 | within_limits | - |
| T-ITT-176 Brook Rd pole | Town of Ithaca (ITH-T) | 75.0 kVA | 61.5 | signal | not calculated | - | review_needed | - |
| T-ITT-177 Ridge Rd pad | Town of Ithaca (ITH-T) | 100.0 kVA | 61.1 | stable | 3.36 (2.59 to 4.13) | 67.1 | within_limits | - |
| T-ITT-178 School Rd pad | Town of Ithaca (ITH-T) | 333.0 kVA | 205.9 | stable | 3.29 (2.54 to 4.04) | 236.4 | within_limits | - |
| T-LAN-005 Triphammer Rd pad | Town of Lansing (LAN) | 167.0 kVA | 129.5 | stable | 1.54 (1.18 to 1.90) | 144.6 | review_needed | - |
| T-LAN-101 Falls Rd pole | Town of Lansing (LAN) | 50.0 kVA | 32.8 | stable | 3.42 (2.64 to 4.21) | 36.1 | within_limits | - |
| T-LAN-102 Station Rd pad | Town of Lansing (LAN) | 250.0 kVA | 169.1 | stable | 2.70 (2.08 to 3.32) | 184.5 | within_limits | - |
| T-LAN-103 Falls Rd pole | Town of Lansing (LAN) | 75.0 kVA | 68.4 | stable | 1.00 (0.75 to 1.24) | 74.4 | review_needed | - |
| T-LAN-104 Creek Rd pole | Town of Lansing (LAN) | 37.5 kVA | 24.8 | stable | 3.28 (2.53 to 4.03) | 28.0 | within_limits | - |
| T-LAN-105 School Rd pad | Town of Lansing (LAN) | 100.0 kVA | 64.2 | stable | 3.86 (2.98 to 4.74) | 71.0 | within_limits | - |
| T-LAN-106 Hill Rd pole | Town of Lansing (LAN) | 37.5 kVA | 26.8 | stable | 3.16 (2.44 to 3.88) | 29.6 | within_limits | - |
| T-LAN-107 Cemetery Rd pad | Town of Lansing (LAN) | 100.0 kVA | 62.6 | stable | 3.24 (2.50 to 3.98) | 69.1 | within_limits | - |
| T-LAN-108 Main St pole | Town of Lansing (LAN) | 75.0 kVA | 49.2 | stable | 3.21 (2.47 to 3.94) | 55.3 | within_limits | - |
| T-LAN-109 Falls Rd pad | Town of Lansing (LAN) | 333.0 kVA | 213.9 | stable | 3.38 (2.61 to 4.15) | 234.9 | within_limits | - |
| T-LAN-110 Station Rd pole | Town of Lansing (LAN) | 37.5 kVA | 34.8 | stable | 0.93 (0.70 to 1.16) | 37.1 | review_needed | - |
| T-LAN-111 Station Rd pole | Town of Lansing (LAN) | 75.0 kVA | 61.5 | signal | not calculated | - | inspect_now | - |
| T-LAN-112 Falls Rd pole | Town of Lansing (LAN) | 50.0 kVA | 32.5 | stable | 3.73 (2.88 to 4.58) | 36.9 | within_limits | - |
| T-LAN-113 Orchard Rd pad | Town of Lansing (LAN) | 100.0 kVA | 65.0 | stable | 3.16 (2.43 to 3.88) | 74.3 | within_limits | - |
| T-LAN-114 Valley Rd pole | Town of Lansing (LAN) | 50.0 kVA | 33.2 | stable | 3.12 (2.40 to 3.83) | 37.7 | within_limits | - |
| T-LAN-115 School Rd pole | Town of Lansing (LAN) | 50.0 kVA | 32.2 | stable | 3.41 (2.63 to 4.19) | 36.3 | within_limits | - |
| T-LAN-116 Hill Rd pole | Town of Lansing (LAN) | 50.0 kVA | 30.7 | stable | 3.76 (2.90 to 4.62) | 35.5 | within_limits | - |
| T-LAN-117 Maple Ave pole | Town of Lansing (LAN) | 75.0 kVA | 49.6 | stable | 3.65 (2.81 to 4.48) | 53.9 | within_limits | - |
| T-LAN-118 Elm St pole | Town of Lansing (LAN) | 75.0 kVA | 47.1 | stable | 3.22 (2.48 to 3.96) | 52.4 | within_limits | - |
| T-LAN-119 Forest Home Dr pad | Town of Lansing (LAN) | 250.0 kVA | 166.9 | stable | 3.27 (2.52 to 4.01) | 185.3 | within_limits | - |
| T-LAN-120 Hanshaw Rd pole | Town of Lansing (LAN) | 50.0 kVA | 41.0 | signal | not calculated | - | review_needed | - |
| T-LAN-121 School Rd pad | Town of Lansing (LAN) | 167.0 kVA | 111.0 | stable | 3.62 (2.79 to 4.45) | 125.4 | within_limits | - |
| T-LAN-122 Hanshaw Rd pad | Town of Lansing (LAN) | 167.0 kVA | 105.9 | stable | 3.29 (2.53 to 4.04) | 117.2 | within_limits | - |
| T-LAN-123 Pine Tree Rd pole | Town of Lansing (LAN) | 37.5 kVA | 23.9 | stable | 2.76 (2.13 to 3.40) | 26.1 | within_limits | - |
| T-LAN-124 Mill St pad | Town of Lansing (LAN) | 167.0 kVA | 110.2 | stable | 3.22 (2.49 to 3.96) | 122.1 | within_limits | - |
| T-LAN-125 Brook Rd pole | Town of Lansing (LAN) | 75.0 kVA | 49.1 | stable | 2.72 (2.09 to 3.34) | 53.7 | within_limits | - |
| T-LAN-126 Maple Ave pad | Town of Lansing (LAN) | 100.0 kVA | 64.4 | stable | 3.03 (2.33 to 3.72) | 74.3 | within_limits | - |
| T-LAN-127 Station Rd pole | Town of Lansing (LAN) | 75.0 kVA | 49.6 | stable | 3.03 (2.34 to 3.73) | 54.3 | within_limits | - |
| T-LAN-128 Church St pad | Town of Lansing (LAN) | 167.0 kVA | 108.5 | stable | 3.15 (2.43 to 3.86) | 120.6 | within_limits | - |
| T-LAN-129 Lake Rd pole | Town of Lansing (LAN) | 50.0 kVA | 31.6 | stable | 3.09 (2.39 to 3.80) | 36.3 | within_limits | - |
| T-LAN-130 Station Rd pole | Town of Lansing (LAN) | 50.0 kVA | 30.6 | stable | 3.27 (2.52 to 4.01) | 33.6 | within_limits | - |
| T-LAN-131 Cemetery Rd pole | Town of Lansing (LAN) | 25.0 kVA | 16.0 | stable | 3.72 (2.87 to 4.57) | 18.4 | within_limits | - |
| T-LAN-132 Orchard Rd pole | Town of Lansing (LAN) | 50.0 kVA | 34.3 | stable | 3.67 (2.83 to 4.51) | 37.8 | within_limits | - |
| T-LAN-133 Hollow Rd pole | Town of Lansing (LAN) | 75.0 kVA | 50.2 | stable | 3.17 (2.45 to 3.90) | 57.7 | within_limits | - |
| T-LAN-134 Hill Rd pad | Town of Lansing (LAN) | 100.0 kVA | 61.5 | stable | 3.60 (2.78 to 4.42) | 68.7 | within_limits | - |
| T-LAN-135 School Rd pole | Town of Lansing (LAN) | 37.5 kVA | 23.4 | stable | 2.97 (2.29 to 3.65) | 26.0 | within_limits | - |
| T-LAN-136 Falls Rd pad | Town of Lansing (LAN) | 250.0 kVA | 159.8 | stable | 3.14 (2.42 to 3.86) | 175.6 | within_limits | - |
| T-LAN-137 Hollow Rd pole | Town of Lansing (LAN) | 37.5 kVA | 27.2 | signal | not calculated | - | inspect_now | - |
| T-LAN-138 School Rd pole | Town of Lansing (LAN) | 75.0 kVA | 48.2 | stable | 2.84 (2.19 to 3.49) | 54.7 | within_limits | - |
| T-LAN-139 Main St pole | Town of Lansing (LAN) | 75.0 kVA | 48.8 | stable | 3.32 (2.56 to 4.08) | 54.8 | within_limits | - |
| T-LAN-140 Station Rd pole | Town of Lansing (LAN) | 50.0 kVA | 32.4 | stable | 3.38 (2.61 to 4.16) | 36.4 | within_limits | - |
| T-LAN-141 Ridge Rd pad | Town of Lansing (LAN) | 167.0 kVA | 107.3 | stable | 3.54 (2.73 to 4.35) | 121.8 | within_limits | - |
| T-LAN-142 Pine Tree Rd pad | Town of Lansing (LAN) | 100.0 kVA | 67.4 | stable | 2.97 (2.29 to 3.65) | 73.3 | within_limits | - |
| T-LAN-143 Valley Rd pole | Town of Lansing (LAN) | 50.0 kVA | 41.0 | signal | not calculated | - | review_needed | - |
| T-LAN-144 Lake Rd pole | Town of Lansing (LAN) | 75.0 kVA | 46.2 | stable | 3.08 (2.37 to 3.78) | 50.9 | within_limits | - |
| T-LAN-145 Valley Rd pad | Town of Lansing (LAN) | 250.0 kVA | 173.2 | stable | 3.55 (2.74 to 4.36) | 196.2 | within_limits | - |
| T-LAN-146 Valley Rd pad | Town of Lansing (LAN) | 250.0 kVA | 163.2 | stable | 3.13 (2.41 to 3.84) | 180.4 | within_limits | - |
| T-LAN-147 Main St pad | Town of Lansing (LAN) | 100.0 kVA | 67.9 | stable | 2.88 (2.22 to 3.54) | 74.0 | within_limits | - |
| T-LAN-148 Mill St pole | Town of Lansing (LAN) | 50.0 kVA | 33.8 | stable | 3.85 (2.97 to 4.73) | 37.0 | within_limits | - |
| T-LAN-149 Brook Rd pad | Town of Lansing (LAN) | 167.0 kVA | 104.3 | stable | 3.13 (2.41 to 3.84) | 117.0 | within_limits | - |
| T-LAN-150 Mill St pad | Town of Lansing (LAN) | 100.0 kVA | 65.5 | stable | 3.17 (2.45 to 3.90) | 72.8 | within_limits | - |
| T-LAN-151 Elm St pole | Town of Lansing (LAN) | 75.0 kVA | 51.2 | stable | 3.28 (2.53 to 4.03) | 55.6 | within_limits | - |
| T-LAN-152 Mill St pad | Town of Lansing (LAN) | 250.0 kVA | 155.8 | stable | 3.24 (2.50 to 3.98) | 180.9 | within_limits | - |
| T-LAN-153 Main St pole | Town of Lansing (LAN) | 37.5 kVA | 25.4 | stable | 2.73 (2.10 to 3.36) | 28.6 | within_limits | - |
| T-LAN-154 Lake Rd pad | Town of Lansing (LAN) | 100.0 kVA | 58.3 | insufficient_history | not calculated | - | review_needed | - |
| T-LAN-155 Mill St pad | Town of Lansing (LAN) | 100.0 kVA | 67.8 | stable | 2.90 (2.24 to 3.56) | 75.9 | within_limits | - |
| T-LAN-156 Brook Rd pole | Town of Lansing (LAN) | 37.5 kVA | 23.3 | stable | 3.47 (2.68 to 4.26) | 26.1 | within_limits | - |
| T-LAN-157 Hill Rd pole | Town of Lansing (LAN) | 50.0 kVA | 35.2 | stable | 2.49 (1.92 to 3.06) | 38.4 | within_limits | - |
| T-LAN-158 Pine Tree Rd pad | Town of Lansing (LAN) | 100.0 kVA | 82.0 | signal | not calculated | - | review_needed | - |
| T-LAN-159 Elm St pad | Town of Lansing (LAN) | 100.0 kVA | 65.1 | stable | 2.95 (2.27 to 3.62) | 72.8 | within_limits | - |
| T-NEW-008 Millard Hill Rd pole | Town of Newfield (NEW) | 50.0 kVA | 33.0 | stable | 2.84 (2.19 to 3.49) | 37.1 | within_limits | - |
| T-NEW-101 Mill St pad | Town of Newfield (NEW) | 250.0 kVA | 163.4 | stable | 3.06 (2.36 to 3.76) | 184.1 | within_limits | - |
| T-NEW-102 Station Rd pole | Town of Newfield (NEW) | 37.5 kVA | 23.7 | stable | 3.84 (2.96 to 4.71) | 26.8 | within_limits | - |
| T-NEW-103 Forest Home Dr pad | Town of Newfield (NEW) | 250.0 kVA | 152.1 | stable | 3.16 (2.43 to 3.88) | 168.3 | within_limits | - |
| T-NEW-104 Brook Rd pole | Town of Newfield (NEW) | 37.5 kVA | 24.4 | stable | 3.47 (2.68 to 4.26) | 27.6 | within_limits | - |
| T-NEW-105 Ridge Rd pad | Town of Newfield (NEW) | 167.0 kVA | 94.9 | insufficient_history | not calculated | - | review_needed | - |
| T-NEW-106 Valley Rd pole | Town of Newfield (NEW) | 75.0 kVA | 47.4 | stable | 3.13 (2.42 to 3.85) | 52.1 | within_limits | - |
| T-NEW-107 Church St pad | Town of Newfield (NEW) | 100.0 kVA | 67.7 | stable | 3.71 (2.86 to 4.55) | 74.0 | within_limits | - |
| T-NEW-108 Forest Home Dr pole | Town of Newfield (NEW) | 50.0 kVA | 35.0 | stable | 2.62 (2.02 to 3.22) | 39.1 | within_limits | - |
| T-NEW-109 Creek Rd pad | Town of Newfield (NEW) | 167.0 kVA | 153.7 | stable | 0.99 (0.75 to 1.23) | 168.8 | review_needed | - |
| T-NEW-110 Creek Rd pole | Town of Newfield (NEW) | 25.0 kVA | 20.5 | stable | 1.55 (1.19 to 1.92) | 21.9 | review_needed | - |
| T-NEW-111 Elm St pad | Town of Newfield (NEW) | 167.0 kVA | 107.4 | stable | 3.49 (2.69 to 4.29) | 121.1 | within_limits | - |
| T-NEW-112 Valley Rd pad | Town of Newfield (NEW) | 100.0 kVA | 82.0 | signal | not calculated | - | review_needed | - |
| T-NEW-113 Ridge Rd pad | Town of Newfield (NEW) | 100.0 kVA | 67.0 | stable | 3.22 (2.48 to 3.96) | 75.5 | within_limits | - |
| T-NEW-114 School Rd pole | Town of Newfield (NEW) | 75.0 kVA | 50.1 | stable | 3.60 (2.78 to 4.43) | 55.0 | within_limits | - |
| T-NEW-115 Valley Rd pad | Town of Newfield (NEW) | 167.0 kVA | 105.3 | stable | 3.04 (2.34 to 3.73) | 115.4 | within_limits | - |
| T-NEW-116 Station Rd pole | Town of Newfield (NEW) | 75.0 kVA | 48.2 | stable | 2.82 (2.18 to 3.47) | 52.4 | within_limits | - |
| T-NEW-117 Maple Ave pole | Town of Newfield (NEW) | 37.5 kVA | 24.6 | stable | 2.80 (2.16 to 3.45) | 27.4 | within_limits | - |
| T-NEW-118 Creek Rd pole | Town of Newfield (NEW) | 50.0 kVA | 30.8 | stable | 3.11 (2.40 to 3.82) | 35.5 | within_limits | - |
| T-NEW-119 Hill Rd pole | Town of Newfield (NEW) | 75.0 kVA | 50.4 | stable | 3.21 (2.48 to 3.94) | 55.9 | within_limits | - |
| T-NEW-120 Cemetery Rd pad | Town of Newfield (NEW) | 333.0 kVA | 206.2 | stable | 3.49 (2.69 to 4.28) | 225.6 | within_limits | - |
| T-NEW-121 Pine Tree Rd pole | Town of Newfield (NEW) | 37.5 kVA | 25.2 | stable | 2.75 (2.12 to 3.38) | 27.8 | within_limits | - |
| T-NEW-122 Pine Tree Rd pad | Town of Newfield (NEW) | 100.0 kVA | 64.2 | stable | 3.39 (2.62 to 4.17) | 70.6 | within_limits | - |
| T-NEW-123 School Rd pole | Town of Newfield (NEW) | 37.5 kVA | 23.7 | stable | 2.66 (2.05 to 3.27) | 26.3 | within_limits | - |
| T-NEW-124 School Rd pad | Town of Newfield (NEW) | 250.0 kVA | 171.8 | stable | 3.68 (2.84 to 4.52) | 187.2 | within_limits | - |
| T-NEW-125 Pine Tree Rd pole | Town of Newfield (NEW) | 50.0 kVA | 32.5 | stable | 3.98 (3.07 to 4.89) | 35.5 | within_limits | - |
| T-TRU-012 Main St pad | Village of Trumansburg (TRU-V) | 100.0 kVA | 82.0 | signal | not calculated | - | inspect_now | - |
| T-TRU-101 Valley Rd pole | Village of Trumansburg (TRU-V) | 50.0 kVA | 31.0 | stable | 3.06 (2.36 to 3.76) | 33.8 | within_limits | - |
| T-TRU-102 Cemetery Rd pad | Village of Trumansburg (TRU-V) | 167.0 kVA | 109.0 | stable | 2.98 (2.30 to 3.66) | 120.9 | within_limits | - |
| T-TRU-103 Ridge Rd pad | Village of Trumansburg (TRU-V) | 100.0 kVA | 82.0 | signal | not calculated | - | review_needed | - |
| T-TRU-104 Brook Rd pole | Village of Trumansburg (TRU-V) | 50.0 kVA | 32.2 | stable | 2.83 (2.18 to 3.48) | 35.4 | within_limits | - |
| T-TRU-105 Brook Rd pole | Village of Trumansburg (TRU-V) | 50.0 kVA | 33.5 | stable | 3.38 (2.60 to 4.15) | 37.9 | within_limits | - |
| T-TRU-106 Creek Rd pole | Village of Trumansburg (TRU-V) | 37.5 kVA | 25.9 | stable | 2.88 (2.22 to 3.54) | 28.2 | within_limits | - |
| T-TRU-107 Main St pole | Village of Trumansburg (TRU-V) | 37.5 kVA | 26.4 | stable | 2.73 (2.10 to 3.36) | 28.8 | within_limits | - |
| T-TRU-108 Hollow Rd pole | Village of Trumansburg (TRU-V) | 25.0 kVA | 15.4 | stable | 3.12 (2.41 to 3.84) | 16.8 | within_limits | - |
| T-TRU-109 Main St pole | Village of Trumansburg (TRU-V) | 25.0 kVA | 15.5 | stable | 3.02 (2.33 to 3.71) | 17.6 | within_limits | - |
| T-TRU-110 Valley Rd pole | Village of Trumansburg (TRU-V) | 50.0 kVA | 34.1 | stable | 3.13 (2.41 to 3.85) | 37.1 | within_limits | - |
| T-ULY-007 Jacksonville Rd pole (new) | Town of Ulysses (ULY) | 75.0 kVA | 45.4 | insufficient_history | not calculated | - | review_needed | - |
| T-ULY-101 Forest Home Dr pad | Town of Ulysses (ULY) | 333.0 kVA | 226.8 | stable | 4.07 (3.14 to 5.00) | 256.8 | within_limits | - |
| T-ULY-102 Ridge Rd pad | Town of Ulysses (ULY) | 167.0 kVA | 101.8 | stable | 3.98 (3.08 to 4.89) | 115.3 | within_limits | - |
| T-ULY-103 Maple Ave pad | Town of Ulysses (ULY) | 250.0 kVA | 156.6 | stable | 3.23 (2.49 to 3.97) | 171.5 | within_limits | - |
| T-ULY-104 Brook Rd pad | Town of Ulysses (ULY) | 250.0 kVA | 166.4 | stable | 3.12 (2.40 to 3.83) | 189.1 | within_limits | - |
| T-ULY-105 Hollow Rd pad | Town of Ulysses (ULY) | 100.0 kVA | 64.5 | stable | 3.56 (2.75 to 4.37) | 73.4 | within_limits | - |
| T-ULY-106 Forest Home Dr pad | Town of Ulysses (ULY) | 167.0 kVA | 107.0 | stable | 2.93 (2.26 to 3.60) | 118.7 | within_limits | - |
| T-ULY-107 Brook Rd pad | Town of Ulysses (ULY) | 100.0 kVA | 82.0 | signal | not calculated | - | inspect_now | - |
| T-ULY-108 Elm St pole | Town of Ulysses (ULY) | 75.0 kVA | 49.7 | stable | 3.00 (2.31 to 3.69) | 54.9 | within_limits | - |
| T-ULY-109 Valley Rd pad | Town of Ulysses (ULY) | 250.0 kVA | 159.4 | stable | 3.42 (2.64 to 4.20) | 174.0 | within_limits | - |
| T-ULY-110 Main St pad | Town of Ulysses (ULY) | 333.0 kVA | 201.2 | insufficient_history | not calculated | - | review_needed | - |
| T-ULY-111 Station Rd pad | Town of Ulysses (ULY) | 167.0 kVA | 103.6 | stable | 3.60 (2.78 to 4.42) | 117.8 | within_limits | - |
| T-ULY-112 Cemetery Rd pad | Town of Ulysses (ULY) | 167.0 kVA | 108.5 | stable | 3.25 (2.51 to 4.00) | 121.5 | within_limits | - |
| T-ULY-113 Cemetery Rd pole | Town of Ulysses (ULY) | 37.5 kVA | 30.8 | signal | not calculated | - | review_needed | - |
| T-ULY-114 Lake Rd pole | Town of Ulysses (ULY) | 37.5 kVA | 30.8 | signal | not calculated | - | review_needed | - |
| T-ULY-115 Hanshaw Rd pad | Town of Ulysses (ULY) | 167.0 kVA | 112.0 | stable | 3.44 (2.65 to 4.23) | 126.5 | within_limits | - |
| T-ULY-116 Ridge Rd pad | Town of Ulysses (ULY) | 167.0 kVA | 136.8 | stable | 1.35 (1.03 to 1.67) | 147.8 | review_needed | - |
| T-ULY-117 Brook Rd pad | Town of Ulysses (ULY) | 100.0 kVA | 68.0 | stable | 3.57 (2.75 to 4.38) | 74.7 | within_limits | - |
| T-ULY-118 Hill Rd pad | Town of Ulysses (ULY) | 100.0 kVA | 66.6 | stable | 3.06 (2.36 to 3.77) | 73.7 | within_limits | - |
| T-ULY-119 Main St pad | Town of Ulysses (ULY) | 100.0 kVA | 64.8 | stable | 3.34 (2.58 to 4.11) | 71.7 | within_limits | - |
| T-ULY-120 Forest Home Dr pole | Town of Ulysses (ULY) | 50.0 kVA | 31.6 | stable | 3.09 (2.39 to 3.80) | 34.9 | within_limits | - |
| T-ULY-121 Maple Ave pole | Town of Ulysses (ULY) | 75.0 kVA | 52.8 | stable | 3.05 (2.36 to 3.75) | 58.4 | within_limits | - |
| T-ULY-122 Cemetery Rd pad | Town of Ulysses (ULY) | 100.0 kVA | 67.1 | stable | 3.00 (2.32 to 3.69) | 75.6 | within_limits | - |
| T-ULY-123 Brook Rd pole | Town of Ulysses (ULY) | 75.0 kVA | 47.9 | stable | 3.39 (2.61 to 4.16) | 53.5 | within_limits | - |
| T-ULY-124 Mill St pole | Town of Ulysses (ULY) | 50.0 kVA | 31.2 | stable | 3.86 (2.98 to 4.74) | 36.1 | within_limits | - |
| T-ULY-125 Brook Rd pole | Town of Ulysses (ULY) | 75.0 kVA | 51.1 | stable | 3.11 (2.40 to 3.83) | 56.1 | within_limits | - |
| T-ULY-126 Elm St pad | Town of Ulysses (ULY) | 167.0 kVA | 106.0 | stable | 3.28 (2.53 to 4.03) | 116.9 | within_limits | - |

### T-CAR-006 Slaterville Rd pole

- Why flagged: rule 11: Forecast peak near or above the rated maximum (0.9 of rating or more)
- Forecast assumptions: {"added_kw": 64.79999999999998, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "CAR", "area_name": "Town of Caroline", "allocation_method": "declared_primary_area", "allocation_flagged": false, "located_areas": ["CAR"], "customers_served": 60, "hp_share_base": 0.12, "hp_share_forecast": 0.57, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-CAR-101 Pine Tree Rd pole

- Why flagged: rule 9: Low Cpk against the rated maximum (playbook threshold 1.33)
- Forecast assumptions: {"added_kw": 26.999999999999996, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "CAR", "area_name": "Town of Caroline", "allocation_method": "declared_primary_area", "allocation_flagged": false, "located_areas": ["CAR"], "customers_served": 25, "hp_share_base": 0.12, "hp_share_forecast": 0.57, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-CAR-102 Orchard Rd pad

- Why flagged: rule 11: Forecast peak near or above the rated maximum (0.9 of rating or more)
- Forecast assumptions: {"added_kw": 58.31999999999999, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "CAR", "area_name": "Town of Caroline", "allocation_method": "declared_primary_area", "allocation_flagged": false, "located_areas": ["CAR"], "customers_served": 54, "hp_share_base": 0.12, "hp_share_forecast": 0.57, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-CAR-103 Cemetery Rd pad

- Why flagged: rule 11: Forecast peak near or above the rated maximum (0.9 of rating or more)
- Forecast assumptions: {"added_kw": 122.03999999999998, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "CAR", "area_name": "Town of Caroline", "allocation_method": "declared_primary_area", "allocation_flagged": true, "located_areas": ["DRY", "CAR"], "customers_served": 113, "hp_share_base": 0.12, "hp_share_forecast": 0.57, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-CAR-104 Pine Tree Rd pad

- Why flagged: rule 1: A reading in the period reached or exceeded the rated maximum
- Chart signal: beyond_3_sigma on 2026-10-13 (value 171.3)
- Chart signal: moving_range_beyond_ucl on 2026-10-13 (value 74.4)
- Chart signal: moving_range_beyond_ucl on 2026-10-14 (value 72.7)
- Forecast assumptions: {"reason_not_projected": "load pattern signal"}
- Disposition: none recorded yet

### T-CAR-105 Pine Tree Rd pole

- Why flagged: rule 11: Forecast peak near or above the rated maximum (0.9 of rating or more)
- Forecast assumptions: {"added_kw": 17.279999999999998, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "CAR", "area_name": "Town of Caroline", "allocation_method": "declared_primary_area", "allocation_flagged": true, "located_areas": ["CAR", "DAN"], "customers_served": 16, "hp_share_base": 0.12, "hp_share_forecast": 0.57, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-CAR-106 Maple Ave pad

- Why flagged: rule 11: Forecast peak near or above the rated maximum (0.9 of rating or more)
- Forecast assumptions: {"added_kw": 49.68, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "CAR", "area_name": "Town of Caroline", "allocation_method": "declared_primary_area", "allocation_flagged": true, "located_areas": ["CAR", "DAN"], "customers_served": 46, "hp_share_base": 0.12, "hp_share_forecast": 0.57, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-CAR-107 Station Rd pole

- Why flagged: rule 11: Forecast peak near or above the rated maximum (0.9 of rating or more)
- Forecast assumptions: {"added_kw": 24.84, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "CAR", "area_name": "Town of Caroline", "allocation_method": "declared_primary_area", "allocation_flagged": true, "located_areas": ["DRY", "CAR"], "customers_served": 23, "hp_share_base": 0.12, "hp_share_forecast": 0.57, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-CAR-108 Church St pad

- Why flagged: rule 9: Low Cpk against the rated maximum (playbook threshold 1.33)
- Forecast assumptions: {"added_kw": 153.35999999999999, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "CAR", "area_name": "Town of Caroline", "allocation_method": "declared_primary_area", "allocation_flagged": false, "located_areas": ["CAR"], "customers_served": 142, "hp_share_base": 0.12, "hp_share_forecast": 0.57, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-CAR-109 Orchard Rd pad

- Why flagged: rule 4: Chart signal: a few outliers; the load pattern may have changed and capability is not calculated until it is explained
- Chart signal: beyond_3_sigma on 2026-10-13 (value 82.0)
- Chart signal: moving_range_beyond_ucl on 2026-10-14 (value 23.5)
- Forecast assumptions: {"reason_not_projected": "load pattern signal"}
- Disposition: none recorded yet

### T-CAR-110 Pine Tree Rd pad

- Why flagged: rule 11: Forecast peak near or above the rated maximum (0.9 of rating or more)
- Forecast assumptions: {"added_kw": 35.63999999999999, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "CAR", "area_name": "Town of Caroline", "allocation_method": "declared_primary_area", "allocation_flagged": false, "located_areas": ["CAR"], "customers_served": 33, "hp_share_base": 0.12, "hp_share_forecast": 0.57, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-CAR-111 Valley Rd pole

- Why flagged: rule 11: Forecast peak near or above the rated maximum (0.9 of rating or more)
- Forecast assumptions: {"added_kw": 38.879999999999995, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "CAR", "area_name": "Town of Caroline", "allocation_method": "declared_primary_area", "allocation_flagged": true, "located_areas": ["CAR", "DAN"], "customers_served": 36, "hp_share_base": 0.12, "hp_share_forecast": 0.57, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-CAR-112 Hollow Rd pad

- Why flagged: rule 11: Forecast peak near or above the rated maximum (0.9 of rating or more)
- Forecast assumptions: {"added_kw": 31.319999999999997, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "CAR", "area_name": "Town of Caroline", "allocation_method": "declared_primary_area", "allocation_flagged": false, "located_areas": ["CAR"], "customers_served": 29, "hp_share_base": 0.12, "hp_share_forecast": 0.57, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-CAR-113 Hollow Rd pole

- Why flagged: rule 11: Forecast peak near or above the rated maximum (0.9 of rating or more)
- Forecast assumptions: {"added_kw": 16.199999999999996, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "CAR", "area_name": "Town of Caroline", "allocation_method": "declared_primary_area", "allocation_flagged": false, "located_areas": ["CAR"], "customers_served": 15, "hp_share_base": 0.12, "hp_share_forecast": 0.57, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-CAR-114 Pine Tree Rd pad

- Why flagged: rule 11: Forecast peak near or above the rated maximum (0.9 of rating or more)
- Forecast assumptions: {"added_kw": 73.44, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "CAR", "area_name": "Town of Caroline", "allocation_method": "declared_primary_area", "allocation_flagged": true, "located_areas": ["DRY", "CAR"], "customers_served": 68, "hp_share_base": 0.12, "hp_share_forecast": 0.57, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-CAR-115 Main St pole

- Why flagged: rule 11: Forecast peak near or above the rated maximum (0.9 of rating or more)
- Forecast assumptions: {"added_kw": 7.559999999999999, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "CAR", "area_name": "Town of Caroline", "allocation_method": "declared_primary_area", "allocation_flagged": true, "located_areas": ["CAR", "DAN"], "customers_served": 7, "hp_share_base": 0.12, "hp_share_forecast": 0.57, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-CAR-116 Station Rd pole

- Why flagged: rule 11: Forecast peak near or above the rated maximum (0.9 of rating or more)
- Forecast assumptions: {"added_kw": 16.199999999999996, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "CAR", "area_name": "Town of Caroline", "allocation_method": "declared_primary_area", "allocation_flagged": false, "located_areas": ["CAR"], "customers_served": 15, "hp_share_base": 0.12, "hp_share_forecast": 0.57, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-CAR-117 Hollow Rd pad

- Why flagged: rule 11: Forecast peak near or above the rated maximum (0.9 of rating or more)
- Forecast assumptions: {"added_kw": 32.39999999999999, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "CAR", "area_name": "Town of Caroline", "allocation_method": "declared_primary_area", "allocation_flagged": true, "located_areas": ["DRY", "CAR"], "customers_served": 30, "hp_share_base": 0.12, "hp_share_forecast": 0.57, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-CAR-118 Brook Rd pad

- Why flagged: rule 5: Not enough stable history to judge the load pattern; a person decides
- Forecast assumptions: {"reason_not_projected": "load pattern insufficient_history"}
- Disposition: none recorded yet

### T-CAR-119 Orchard Rd pole

- Why flagged: rule 11: Forecast peak near or above the rated maximum (0.9 of rating or more)
- Forecast assumptions: {"added_kw": 20.519999999999996, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "CAR", "area_name": "Town of Caroline", "allocation_method": "declared_primary_area", "allocation_flagged": false, "located_areas": ["CAR"], "customers_served": 19, "hp_share_base": 0.12, "hp_share_forecast": 0.57, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-CAR-120 Brook Rd pad

- Why flagged: rule 11: Forecast peak near or above the rated maximum (0.9 of rating or more)
- Forecast assumptions: {"added_kw": 32.39999999999999, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "CAR", "area_name": "Town of Caroline", "allocation_method": "declared_primary_area", "allocation_flagged": false, "located_areas": ["CAR"], "customers_served": 30, "hp_share_base": 0.12, "hp_share_forecast": 0.57, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-CAR-121 Lake Rd pole

- Why flagged: rule 11: Forecast peak near or above the rated maximum (0.9 of rating or more)
- Forecast assumptions: {"added_kw": 19.439999999999998, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "CAR", "area_name": "Town of Caroline", "allocation_method": "declared_primary_area", "allocation_flagged": false, "located_areas": ["CAR"], "customers_served": 18, "hp_share_base": 0.12, "hp_share_forecast": 0.57, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-CAR-122 Elm St pole

- Why flagged: rule 11: Forecast peak near or above the rated maximum (0.9 of rating or more)
- Forecast assumptions: {"added_kw": 31.319999999999997, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "CAR", "area_name": "Town of Caroline", "allocation_method": "declared_primary_area", "allocation_flagged": false, "located_areas": ["CAR"], "customers_served": 29, "hp_share_base": 0.12, "hp_share_forecast": 0.57, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-CAR-123 Elm St pole

- Why flagged: rule 11: Forecast peak near or above the rated maximum (0.9 of rating or more)
- Forecast assumptions: {"added_kw": 18.36, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "CAR", "area_name": "Town of Caroline", "allocation_method": "declared_primary_area", "allocation_flagged": false, "located_areas": ["CAR"], "customers_served": 17, "hp_share_base": 0.12, "hp_share_forecast": 0.57, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-CAR-124 School Rd pole

- Why flagged: rule 11: Forecast peak near or above the rated maximum (0.9 of rating or more)
- Forecast assumptions: {"added_kw": 8.639999999999999, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "CAR", "area_name": "Town of Caroline", "allocation_method": "declared_primary_area", "allocation_flagged": false, "located_areas": ["CAR"], "customers_served": 8, "hp_share_base": 0.12, "hp_share_forecast": 0.57, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-CAY-103 Ridge Rd pad

- Why flagged: rule 10: Uncertain Cpk: the lower 95% confidence bound is below 1.33
- Forecast assumptions: {"added_kw": 5.760000000000001, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "CAY-V", "area_name": "Village of Cayuga Heights", "allocation_method": "declared_primary_area", "allocation_flagged": true, "located_areas": ["ITH-C", "ITH-T", "CAY-V"], "customers_served": 30, "hp_share_base": 0.12, "hp_share_forecast": 0.2, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-CAY-114 Main St pole

- Why flagged: rule 9: Low Cpk against the rated maximum (playbook threshold 1.33)
- Forecast assumptions: {"added_kw": 6.7200000000000015, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "CAY-V", "area_name": "Village of Cayuga Heights", "allocation_method": "declared_primary_area", "allocation_flagged": true, "located_areas": ["ITH-T", "CAY-V", "LAN"], "customers_served": 35, "hp_share_base": 0.12, "hp_share_forecast": 0.2, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-DAN-010 Comfort Rd pole

- Why flagged: rule 9: Low Cpk against the rated maximum (playbook threshold 1.33)
- Forecast assumptions: {"added_kw": 4.224, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "DAN", "area_name": "Town of Danby", "allocation_method": "declared_primary_area", "allocation_flagged": false, "located_areas": ["DAN"], "customers_served": 22, "hp_share_base": 0.12, "hp_share_forecast": 0.2, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-DAN-101 Hollow Rd pad

- Why flagged: rule 4: Chart signal: a few outliers; the load pattern may have changed and capability is not calculated until it is explained
- Chart signal: beyond_3_sigma on 2026-10-13 (value 136.9)
- Chart signal: moving_range_beyond_ucl on 2026-10-13 (value 34.9)
- Chart signal: moving_range_beyond_ucl on 2026-10-14 (value 43.8)
- Forecast assumptions: {"reason_not_projected": "load pattern signal"}
- Disposition: none recorded yet

### T-DAN-110 School Rd pad

- Why flagged: rule 4: Chart signal: a few outliers; the load pattern may have changed and capability is not calculated until it is explained
- Chart signal: beyond_3_sigma on 2026-10-13 (value 82.0)
- Chart signal: moving_range_beyond_ucl on 2026-10-13 (value 22.6)
- Chart signal: moving_range_beyond_ucl on 2026-10-14 (value 22.7)
- Forecast assumptions: {"reason_not_projected": "load pattern signal"}
- Disposition: none recorded yet

### T-DAN-111 Ridge Rd pole

- Why flagged: rule 1: A reading in the period reached or exceeded the rated maximum
- Chart signal: beyond_3_sigma on 2026-10-13 (value 39.6)
- Chart signal: moving_range_beyond_ucl on 2026-10-13 (value 13.9)
- Chart signal: moving_range_beyond_ucl on 2026-10-14 (value 13.8)
- Forecast assumptions: {"reason_not_projected": "load pattern signal"}
- Disposition: none recorded yet

### T-DAN-112 School Rd pole

- Why flagged: rule 3: Repeated outliers this period (3 or more days beyond 3 sigma or with a moving-range spike)
- Chart signal: beyond_3_sigma on 2026-10-10 (value 61.5)
- Chart signal: beyond_3_sigma on 2026-10-12 (value 28.5)
- Chart signal: beyond_3_sigma on 2026-10-14 (value 61.5)
- Chart signal: moving_range_beyond_ucl on 2026-10-10 (value 18.4)
- Chart signal: moving_range_beyond_ucl on 2026-10-11 (value 15.4)
- Chart signal: moving_range_beyond_ucl on 2026-10-12 (value 17.6)
- Chart signal: moving_range_beyond_ucl on 2026-10-13 (value 17.7)
- Chart signal: moving_range_beyond_ucl on 2026-10-14 (value 15.3)
- Chart signal: moving_range_beyond_ucl on 2026-10-15 (value 14.0)
- Forecast assumptions: {"reason_not_projected": "load pattern signal"}
- Disposition: none recorded yet

### T-DAN-113 Hill Rd pole

- Why flagged: rule 9: Low Cpk against the rated maximum (playbook threshold 1.33)
- Forecast assumptions: {"added_kw": 3.0720000000000005, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "DAN", "area_name": "Town of Danby", "allocation_method": "declared_primary_area", "allocation_flagged": false, "located_areas": ["DAN"], "customers_served": 16, "hp_share_base": 0.12, "hp_share_forecast": 0.2, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-DAN-114 Falls Rd pole

- Why flagged: rule 5: Not enough stable history to judge the load pattern; a person decides
- Forecast assumptions: {"reason_not_projected": "load pattern insufficient_history"}
- Disposition: none recorded yet

### T-DAN-120 Lake Rd pole

- Why flagged: rule 4: Chart signal: a few outliers; the load pattern may have changed and capability is not calculated until it is explained
- Chart signal: beyond_3_sigma on 2026-10-13 (value 41.0)
- Chart signal: moving_range_beyond_ucl on 2026-10-13 (value 11.6)
- Chart signal: moving_range_beyond_ucl on 2026-10-14 (value 10.0)
- Forecast assumptions: {"reason_not_projected": "load pattern signal"}
- Disposition: none recorded yet

### T-DAN-124 Brook Rd pole

- Why flagged: rule 3: Repeated outliers this period (3 or more days beyond 3 sigma or with a moving-range spike)
- Chart signal: beyond_3_sigma on 2026-10-10 (value 41.0)
- Chart signal: beyond_3_sigma on 2026-10-12 (value 19.0)
- Chart signal: beyond_3_sigma on 2026-10-14 (value 41.0)
- Chart signal: moving_range_beyond_ucl on 2026-10-10 (value 12.0)
- Chart signal: moving_range_beyond_ucl on 2026-10-11 (value 11.2)
- Chart signal: moving_range_beyond_ucl on 2026-10-12 (value 10.8)
- Chart signal: moving_range_beyond_ucl on 2026-10-13 (value 14.1)
- Chart signal: moving_range_beyond_ucl on 2026-10-15 (value 12.9)
- Forecast assumptions: {"reason_not_projected": "load pattern signal"}
- Disposition: none recorded yet

### T-DRY-004 Freeville Rd pole

- Why flagged: rule 4: Chart signal: a few outliers; the load pattern may have changed and capability is not calculated until it is explained
- Chart signal: beyond_3_sigma on 2026-10-13 (value 61.5)
- Chart signal: moving_range_beyond_ucl on 2026-10-13 (value 16.9)
- Chart signal: moving_range_beyond_ucl on 2026-10-14 (value 16.5)
- Forecast assumptions: {"reason_not_projected": "load pattern signal"}
- Disposition: none recorded yet

### T-DRY-107 Elm St pad

- Why flagged: rule 10: Uncertain Cpk: the lower 95% confidence bound is below 1.33
- Forecast assumptions: {"added_kw": 5.376, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "DRY", "area_name": "Town of Dryden", "allocation_method": "declared_primary_area", "allocation_flagged": true, "located_areas": ["DRY", "GRO"], "customers_served": 28, "hp_share_base": 0.12, "hp_share_forecast": 0.2, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-DRY-111 Hollow Rd pad

- Why flagged: rule 10: Uncertain Cpk: the lower 95% confidence bound is below 1.33
- Forecast assumptions: {"added_kw": 7.872000000000002, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "DRY", "area_name": "Town of Dryden", "allocation_method": "declared_primary_area", "allocation_flagged": true, "located_areas": ["DRY", "CAR"], "customers_served": 41, "hp_share_base": 0.12, "hp_share_forecast": 0.2, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-DRY-116 Lake Rd pole

- Why flagged: rule 9: Low Cpk against the rated maximum (playbook threshold 1.33)
- Forecast assumptions: {"added_kw": 4.416, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "DRY", "area_name": "Town of Dryden", "allocation_method": "declared_primary_area", "allocation_flagged": false, "located_areas": ["DRY"], "customers_served": 23, "hp_share_base": 0.12, "hp_share_forecast": 0.2, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-DRY-123 Brook Rd pad

- Why flagged: rule 9: Low Cpk against the rated maximum (playbook threshold 1.33)
- Forecast assumptions: {"added_kw": 5.760000000000001, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "DRY", "area_name": "Town of Dryden", "allocation_method": "declared_primary_area", "allocation_flagged": false, "located_areas": ["DRY"], "customers_served": 30, "hp_share_base": 0.12, "hp_share_forecast": 0.2, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-DRY-125 Creek Rd pole

- Why flagged: rule 9: Low Cpk against the rated maximum (playbook threshold 1.33)
- Forecast assumptions: {"added_kw": 4.800000000000001, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "DRY", "area_name": "Town of Dryden", "allocation_method": "declared_primary_area", "allocation_flagged": false, "located_areas": ["DRY"], "customers_served": 25, "hp_share_base": 0.12, "hp_share_forecast": 0.2, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-DRY-129 Cemetery Rd pad

- Why flagged: rule 3: Repeated outliers this period (3 or more days beyond 3 sigma or with a moving-range spike)
- Chart signal: beyond_3_sigma on 2026-10-10 (value 205.0)
- Chart signal: beyond_3_sigma on 2026-10-12 (value 95.0)
- Chart signal: beyond_3_sigma on 2026-10-14 (value 205.0)
- Chart signal: moving_range_beyond_ucl on 2026-10-10 (value 55.4)
- Chart signal: moving_range_beyond_ucl on 2026-10-11 (value 45.8)
- Chart signal: moving_range_beyond_ucl on 2026-10-12 (value 64.2)
- Chart signal: moving_range_beyond_ucl on 2026-10-13 (value 58.4)
- Chart signal: moving_range_beyond_ucl on 2026-10-14 (value 51.6)
- Chart signal: moving_range_beyond_ucl on 2026-10-15 (value 49.4)
- Forecast assumptions: {"reason_not_projected": "load pattern signal"}
- Disposition: none recorded yet

### T-DRY-131 Cemetery Rd pole

- Why flagged: rule 4: Chart signal: a few outliers; the load pattern may have changed and capability is not calculated until it is explained
- Chart signal: beyond_3_sigma on 2026-10-13 (value 52.3)
- Forecast assumptions: {"reason_not_projected": "load pattern signal"}
- Disposition: none recorded yet

### T-DRY-135 Lake Rd pad

- Why flagged: rule 2: Sustained shift this period: a run rule fired (8 in a row on one side of the centre line or 2 of 3 beyond 2 sigma)
- Chart signal: two_of_three_beyond_2_sigma on 2026-10-08 (value 116.1)
- Chart signal: two_of_three_beyond_2_sigma on 2026-10-09 (value 115.4)
- Chart signal: two_of_three_beyond_2_sigma on 2026-10-10 (value 115.8)
- Chart signal: two_of_three_beyond_2_sigma on 2026-10-11 (value 110.0)
- Chart signal: two_of_three_beyond_2_sigma on 2026-10-12 (value 119.7)
- Chart signal: two_of_three_beyond_2_sigma on 2026-10-13 (value 120.2)
- Chart signal: two_of_three_beyond_2_sigma on 2026-10-14 (value 101.0)
- Chart signal: eight_in_a_row_one_side on 2026-10-13 (value 120.2)
- Forecast assumptions: {"reason_not_projected": "load pattern signal"}
- Disposition: none recorded yet

### T-DRY-141 Forest Home Dr pad

- Why flagged: rule 2: Sustained shift this period: a run rule fired (8 in a row on one side of the centre line or 2 of 3 beyond 2 sigma)
- Chart signal: two_of_three_beyond_2_sigma on 2026-10-07 (value 71.9)
- Chart signal: two_of_three_beyond_2_sigma on 2026-10-08 (value 69.6)
- Chart signal: two_of_three_beyond_2_sigma on 2026-10-09 (value 69.8)
- Chart signal: two_of_three_beyond_2_sigma on 2026-10-10 (value 66.6)
- Chart signal: eight_in_a_row_one_side on 2026-10-12 (value 70.4)
- Forecast assumptions: {"reason_not_projected": "load pattern signal"}
- Disposition: none recorded yet

### T-DRY-145 Creek Rd pole

- Why flagged: rule 4: Chart signal: a few outliers; the load pattern may have changed and capability is not calculated until it is explained
- Chart signal: beyond_3_sigma on 2026-10-13 (value 61.5)
- Chart signal: moving_range_beyond_ucl on 2026-10-13 (value 14.6)
- Chart signal: moving_range_beyond_ucl on 2026-10-14 (value 19.0)
- Forecast assumptions: {"reason_not_projected": "load pattern signal"}
- Disposition: none recorded yet

### T-ENF-011 Mecklenburg Rd pole

- Why flagged: rule 1: A reading in the period reached or exceeded the rated maximum
- Chart signal: beyond_3_sigma on 2026-10-13 (value 78.7)
- Chart signal: moving_range_beyond_ucl on 2026-10-13 (value 29.5)
- Chart signal: moving_range_beyond_ucl on 2026-10-14 (value 31.3)
- Forecast assumptions: {"reason_not_projected": "load pattern signal"}
- Disposition: none recorded yet

### T-ENF-101 Falls Rd pad

- Why flagged: rule 4: Chart signal: a few outliers; the load pattern may have changed and capability is not calculated until it is explained
- Chart signal: beyond_3_sigma on 2026-10-13 (value 82.0)
- Chart signal: moving_range_beyond_ucl on 2026-10-13 (value 23.7)
- Chart signal: moving_range_beyond_ucl on 2026-10-14 (value 24.5)
- Forecast assumptions: {"reason_not_projected": "load pattern signal"}
- Disposition: none recorded yet

### T-ENF-103 School Rd pole

- Why flagged: rule 5: Not enough stable history to judge the load pattern; a person decides
- Forecast assumptions: {"reason_not_projected": "load pattern insufficient_history"}
- Disposition: none recorded yet

### T-ENF-107 School Rd pad

- Why flagged: rule 1: A reading in the period reached or exceeded the rated maximum
- Chart signal: beyond_3_sigma on 2026-10-13 (value 348.6)
- Chart signal: moving_range_beyond_ucl on 2026-10-13 (value 155.0)
- Chart signal: moving_range_beyond_ucl on 2026-10-14 (value 153.3)
- Forecast assumptions: {"reason_not_projected": "load pattern signal"}
- Disposition: none recorded yet

### T-ENF-112 Falls Rd pole

- Why flagged: rule 10: Uncertain Cpk: the lower 95% confidence bound is below 1.33
- Forecast assumptions: {"added_kw": 2.8800000000000003, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "ENF", "area_name": "Town of Enfield", "allocation_method": "declared_primary_area", "allocation_flagged": true, "located_areas": ["ITH-T", "ENF"], "customers_served": 15, "hp_share_base": 0.12, "hp_share_forecast": 0.2, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-GRO-009 Peruville Rd pad

- Why flagged: rule 2: Sustained shift this period: a run rule fired (8 in a row on one side of the centre line or 2 of 3 beyond 2 sigma)
- Chart signal: beyond_3_sigma on 2026-10-07 (value 71.4)
- Chart signal: beyond_3_sigma on 2026-10-08 (value 71.5)
- Chart signal: beyond_3_sigma on 2026-10-09 (value 71.5)
- Chart signal: two_of_three_beyond_2_sigma on 2026-10-07 (value 71.4)
- Chart signal: two_of_three_beyond_2_sigma on 2026-10-08 (value 71.5)
- Chart signal: two_of_three_beyond_2_sigma on 2026-10-09 (value 71.5)
- Chart signal: two_of_three_beyond_2_sigma on 2026-10-10 (value 64.3)
- Chart signal: two_of_three_beyond_2_sigma on 2026-10-11 (value 68.7)
- Chart signal: two_of_three_beyond_2_sigma on 2026-10-13 (value 69.0)
- Chart signal: eight_in_a_row_one_side on 2026-10-12 (value 66.0)
- Forecast assumptions: {"reason_not_projected": "load pattern signal"}
- Disposition: none recorded yet

### T-GRO-106 Hill Rd pole

- Why flagged: rule 4: Chart signal: a few outliers; the load pattern may have changed and capability is not calculated until it is explained
- Chart signal: beyond_3_sigma on 2026-10-13 (value 30.8)
- Chart signal: moving_range_beyond_ucl on 2026-10-13 (value 9.6)
- Chart signal: moving_range_beyond_ucl on 2026-10-14 (value 7.0)
- Forecast assumptions: {"reason_not_projected": "load pattern signal"}
- Disposition: none recorded yet

### T-GRO-114 Station Rd pole

- Why flagged: rule 4: Chart signal: a few outliers; the load pattern may have changed and capability is not calculated until it is explained
- Chart signal: beyond_3_sigma on 2026-10-13 (value 61.5)
- Chart signal: moving_range_beyond_ucl on 2026-10-13 (value 19.8)
- Chart signal: moving_range_beyond_ucl on 2026-10-14 (value 16.9)
- Forecast assumptions: {"reason_not_projected": "load pattern signal"}
- Disposition: none recorded yet

### T-GRO-118 Main St pole

- Why flagged: rule 1: A reading in the period reached or exceeded the rated maximum
- Chart signal: beyond_3_sigma on 2026-10-13 (value 77.2)
- Chart signal: moving_range_beyond_ucl on 2026-10-13 (value 32.7)
- Chart signal: moving_range_beyond_ucl on 2026-10-14 (value 28.3)
- Forecast assumptions: {"reason_not_projected": "load pattern signal"}
- Disposition: none recorded yet

### T-GRO-135 Mill St pad

- Why flagged: rule 9: Low Cpk against the rated maximum (playbook threshold 1.33)
- Forecast assumptions: {"added_kw": 21.504, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "GRO", "area_name": "Town of Groton", "allocation_method": "declared_primary_area", "allocation_flagged": true, "located_areas": ["DRY", "GRO"], "customers_served": 112, "hp_share_base": 0.12, "hp_share_forecast": 0.2, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-ITC-102 Forest Home Dr pole

- Why flagged: rule 9: Low Cpk against the rated maximum (playbook threshold 1.33)
- Forecast assumptions: {"added_kw": 3.6480000000000006, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "ITH-C", "area_name": "City of Ithaca", "allocation_method": "declared_primary_area", "allocation_flagged": true, "located_areas": ["ITH-C", "ITH-T", "NEW"], "customers_served": 19, "hp_share_base": 0.12, "hp_share_forecast": 0.2, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-ITC-104 Pine Tree Rd pad

- Why flagged: rule 2: Sustained shift this period: a run rule fired (8 in a row on one side of the centre line or 2 of 3 beyond 2 sigma)
- Chart signal: two_of_three_beyond_2_sigma on 2026-10-13 (value 118.8)
- Chart signal: two_of_three_beyond_2_sigma on 2026-10-14 (value 107.6)
- Chart signal: eight_in_a_row_one_side on 2026-10-13 (value 118.8)
- Forecast assumptions: {"reason_not_projected": "load pattern signal"}
- Disposition: none recorded yet

### T-ITC-106 Station Rd pole

- Why flagged: rule 10: Uncertain Cpk: the lower 95% confidence bound is below 1.33
- Forecast assumptions: {"added_kw": 1.5360000000000003, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "ITH-C", "area_name": "City of Ithaca", "allocation_method": "declared_primary_area", "allocation_flagged": true, "located_areas": ["ITH-C", "ITH-T"], "customers_served": 8, "hp_share_base": 0.12, "hp_share_forecast": 0.2, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-ITC-114 Brook Rd pad

- Why flagged: rule 9: Low Cpk against the rated maximum (playbook threshold 1.33)
- Forecast assumptions: {"added_kw": 18.048000000000002, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "ITH-C", "area_name": "City of Ithaca", "allocation_method": "declared_primary_area", "allocation_flagged": true, "located_areas": ["ITH-C", "ITH-T"], "customers_served": 94, "hp_share_base": 0.12, "hp_share_forecast": 0.2, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-ITC-122 Station Rd pole

- Why flagged: rule 4: Chart signal: a few outliers; the load pattern may have changed and capability is not calculated until it is explained
- Chart signal: beyond_3_sigma on 2026-10-13 (value 41.0)
- Chart signal: moving_range_beyond_ucl on 2026-10-13 (value 11.8)
- Chart signal: moving_range_beyond_ucl on 2026-10-14 (value 11.6)
- Forecast assumptions: {"reason_not_projected": "load pattern signal"}
- Disposition: none recorded yet

### T-ITC-124 Valley Rd pole

- Why flagged: rule 10: Uncertain Cpk: the lower 95% confidence bound is below 1.33
- Forecast assumptions: {"added_kw": 3.6480000000000006, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "ITH-C", "area_name": "City of Ithaca", "allocation_method": "declared_primary_area", "allocation_flagged": true, "located_areas": ["ITH-C", "ITH-T"], "customers_served": 19, "hp_share_base": 0.12, "hp_share_forecast": 0.2, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-ITC-127 Hanshaw Rd pad

- Why flagged: rule 4: Chart signal: a few outliers; the load pattern may have changed and capability is not calculated until it is explained
- Chart signal: beyond_3_sigma on 2026-10-13 (value 82.0)
- Chart signal: moving_range_beyond_ucl on 2026-10-14 (value 19.0)
- Forecast assumptions: {"reason_not_projected": "load pattern signal"}
- Disposition: none recorded yet

### T-ITC-128 Maple Ave pad

- Why flagged: rule 9: Low Cpk against the rated maximum (playbook threshold 1.33)
- Forecast assumptions: {"added_kw": 9.408000000000001, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "ITH-C", "area_name": "City of Ithaca", "allocation_method": "declared_primary_area", "allocation_flagged": true, "located_areas": ["ITH-C", "ITH-T"], "customers_served": 49, "hp_share_base": 0.12, "hp_share_forecast": 0.2, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-ITC-133 Maple Ave pad

- Why flagged: rule 10: Uncertain Cpk: the lower 95% confidence bound is below 1.33
- Forecast assumptions: {"added_kw": 29.568000000000005, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "ITH-C", "area_name": "City of Ithaca", "allocation_method": "declared_primary_area", "allocation_flagged": true, "located_areas": ["ITH-C", "ITH-T"], "customers_served": 154, "hp_share_base": 0.12, "hp_share_forecast": 0.2, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-ITC-134 Elm St pole

- Why flagged: rule 9: Low Cpk against the rated maximum (playbook threshold 1.33)
- Forecast assumptions: {"added_kw": 2.8800000000000003, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "ITH-C", "area_name": "City of Ithaca", "allocation_method": "declared_primary_area", "allocation_flagged": true, "located_areas": ["ITH-C", "ITH-T"], "customers_served": 15, "hp_share_base": 0.12, "hp_share_forecast": 0.2, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-ITC-135 Creek Rd pad

- Why flagged: rule 1: A reading in the period reached or exceeded the rated maximum
- Chart signal: beyond_3_sigma on 2026-10-13 (value 104.8)
- Chart signal: moving_range_beyond_ucl on 2026-10-13 (value 49.7)
- Chart signal: moving_range_beyond_ucl on 2026-10-14 (value 40.6)
- Forecast assumptions: {"reason_not_projected": "load pattern signal"}
- Disposition: none recorded yet

### T-ITC-139 Brook Rd pole

- Why flagged: rule 10: Uncertain Cpk: the lower 95% confidence bound is below 1.33
- Forecast assumptions: {"added_kw": 1.5360000000000003, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "ITH-C", "area_name": "City of Ithaca", "allocation_method": "declared_primary_area", "allocation_flagged": true, "located_areas": ["ITH-C", "ITH-T"], "customers_served": 8, "hp_share_base": 0.12, "hp_share_forecast": 0.2, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-ITC-140 Maple Ave pole

- Why flagged: rule 5: Not enough stable history to judge the load pattern; a person decides
- Forecast assumptions: {"reason_not_projected": "load pattern insufficient_history"}
- Disposition: none recorded yet

### T-ITC-145 Hill Rd pole

- Why flagged: rule 4: Chart signal: a few outliers; the load pattern may have changed and capability is not calculated until it is explained
- Chart signal: beyond_3_sigma on 2026-10-13 (value 41.0)
- Chart signal: moving_range_beyond_ucl on 2026-10-13 (value 12.4)
- Chart signal: moving_range_beyond_ucl on 2026-10-14 (value 8.4)
- Forecast assumptions: {"reason_not_projected": "load pattern signal"}
- Disposition: none recorded yet

### T-ITC-147 Cemetery Rd pad

- Why flagged: rule 4: Chart signal: a few outliers; the load pattern may have changed and capability is not calculated until it is explained
- Chart signal: beyond_3_sigma on 2026-10-13 (value 205.0)
- Chart signal: moving_range_beyond_ucl on 2026-10-13 (value 50.1)
- Chart signal: moving_range_beyond_ucl on 2026-10-14 (value 50.2)
- Forecast assumptions: {"reason_not_projected": "load pattern signal"}
- Disposition: none recorded yet

### T-ITC-150 Orchard Rd pole

- Why flagged: rule 1: A reading in the period reached or exceeded the rated maximum
- Chart signal: beyond_3_sigma on 2026-10-13 (value 79.5)
- Chart signal: moving_range_beyond_ucl on 2026-10-13 (value 38.3)
- Chart signal: moving_range_beyond_ucl on 2026-10-14 (value 36.6)
- Forecast assumptions: {"reason_not_projected": "load pattern signal"}
- Disposition: none recorded yet

### T-ITC-159 Valley Rd pad

- Why flagged: rule 9: Low Cpk against the rated maximum (playbook threshold 1.33)
- Forecast assumptions: {"added_kw": 9.792000000000002, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "ITH-C", "area_name": "City of Ithaca", "allocation_method": "declared_primary_area", "allocation_flagged": true, "located_areas": ["ITH-C", "ITH-T"], "customers_served": 51, "hp_share_base": 0.12, "hp_share_forecast": 0.2, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-ITC-173 Hill Rd pole

- Why flagged: rule 4: Chart signal: a few outliers; the load pattern may have changed and capability is not calculated until it is explained
- Chart signal: beyond_3_sigma on 2026-10-13 (value 41.0)
- Chart signal: moving_range_beyond_ucl on 2026-10-14 (value 11.4)
- Forecast assumptions: {"reason_not_projected": "load pattern signal"}
- Disposition: none recorded yet

### T-ITC-183 Mill St pole

- Why flagged: rule 9: Low Cpk against the rated maximum (playbook threshold 1.33)
- Forecast assumptions: {"added_kw": 3.0720000000000005, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "ITH-C", "area_name": "City of Ithaca", "allocation_method": "declared_primary_area", "allocation_flagged": true, "located_areas": ["ITH-C", "ITH-T"], "customers_served": 16, "hp_share_base": 0.12, "hp_share_forecast": 0.2, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-ITC-190 Forest Home Dr pad

- Why flagged: rule 1: A reading in the period reached or exceeded the rated maximum
- Chart signal: beyond_3_sigma on 2026-10-13 (value 104.5)
- Chart signal: moving_range_beyond_ucl on 2026-10-13 (value 45.9)
- Chart signal: moving_range_beyond_ucl on 2026-10-14 (value 42.4)
- Forecast assumptions: {"reason_not_projected": "load pattern signal"}
- Disposition: none recorded yet

### T-ITC-192 Elm St pad

- Why flagged: rule 10: Uncertain Cpk: the lower 95% confidence bound is below 1.33
- Forecast assumptions: {"added_kw": 14.592000000000002, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "ITH-C", "area_name": "City of Ithaca", "allocation_method": "declared_primary_area", "allocation_flagged": true, "located_areas": ["ITH-C", "ITH-T"], "customers_served": 76, "hp_share_base": 0.12, "hp_share_forecast": 0.2, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-ITC-193 Cemetery Rd pole

- Why flagged: rule 9: Low Cpk against the rated maximum (playbook threshold 1.33)
- Forecast assumptions: {"added_kw": 2.688, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "ITH-C", "area_name": "City of Ithaca", "allocation_method": "declared_primary_area", "allocation_flagged": true, "located_areas": ["ITH-C", "ITH-T"], "customers_served": 14, "hp_share_base": 0.12, "hp_share_forecast": 0.2, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-ITC-194 Mill St pad

- Why flagged: rule 1: A reading in the period reached or exceeded the rated maximum
- Chart signal: beyond_3_sigma on 2026-10-13 (value 351.4)
- Chart signal: moving_range_beyond_ucl on 2026-10-13 (value 149.4)
- Chart signal: moving_range_beyond_ucl on 2026-10-14 (value 155.3)
- Forecast assumptions: {"reason_not_projected": "load pattern signal"}
- Disposition: none recorded yet

### T-ITC-198 Brook Rd pad

- Why flagged: rule 5: Not enough stable history to judge the load pattern; a person decides
- Forecast assumptions: {"reason_not_projected": "load pattern insufficient_history"}
- Disposition: none recorded yet

### T-ITC-200 Cemetery Rd pad

- Why flagged: rule 4: Chart signal: a few outliers; the load pattern may have changed and capability is not calculated until it is explained
- Chart signal: beyond_3_sigma on 2026-10-13 (value 82.0)
- Chart signal: moving_range_beyond_ucl on 2026-10-13 (value 21.2)
- Chart signal: moving_range_beyond_ucl on 2026-10-14 (value 25.6)
- Forecast assumptions: {"reason_not_projected": "load pattern signal"}
- Disposition: none recorded yet

### T-ITT-108 Hanshaw Rd pole

- Why flagged: rule 10: Uncertain Cpk: the lower 95% confidence bound is below 1.33
- Forecast assumptions: {"added_kw": 2.112, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "ITH-T", "area_name": "Town of Ithaca", "allocation_method": "declared_primary_area", "allocation_flagged": true, "located_areas": ["ITH-T", "CAY-V"], "customers_served": 11, "hp_share_base": 0.12, "hp_share_forecast": 0.2, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-ITT-113 Orchard Rd pole

- Why flagged: rule 9: Low Cpk against the rated maximum (playbook threshold 1.33)
- Forecast assumptions: {"added_kw": 2.3040000000000003, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "ITH-T", "area_name": "Town of Ithaca", "allocation_method": "declared_primary_area", "allocation_flagged": true, "located_areas": ["ITH-T", "DAN"], "customers_served": 12, "hp_share_base": 0.12, "hp_share_forecast": 0.2, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-ITT-120 Forest Home Dr pole

- Why flagged: rule 9: Low Cpk against the rated maximum (playbook threshold 1.33)
- Forecast assumptions: {"added_kw": 3.8400000000000007, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "ITH-T", "area_name": "Town of Ithaca", "allocation_method": "declared_primary_area", "allocation_flagged": true, "located_areas": ["ITH-T", "ENF"], "customers_served": 20, "hp_share_base": 0.12, "hp_share_forecast": 0.2, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-ITT-121 Creek Rd pole

- Why flagged: rule 9: Low Cpk against the rated maximum (playbook threshold 1.33)
- Forecast assumptions: {"added_kw": 1.5360000000000003, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "ITH-T", "area_name": "Town of Ithaca", "allocation_method": "declared_primary_area", "allocation_flagged": true, "located_areas": ["ITH-T", "DAN", "NEW"], "customers_served": 8, "hp_share_base": 0.12, "hp_share_forecast": 0.2, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-ITT-124 Forest Home Dr pole

- Why flagged: rule 2: Sustained shift this period: a run rule fired (8 in a row on one side of the centre line or 2 of 3 beyond 2 sigma)
- Chart signal: eight_in_a_row_one_side on 2026-10-11 (value 49.8)
- Forecast assumptions: {"reason_not_projected": "load pattern signal"}
- Disposition: none recorded yet

### T-ITT-127 Church St pad

- Why flagged: rule 9: Low Cpk against the rated maximum (playbook threshold 1.33)
- Forecast assumptions: {"added_kw": 14.208000000000002, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "ITH-T", "area_name": "Town of Ithaca", "allocation_method": "declared_primary_area", "allocation_flagged": false, "located_areas": ["ITH-T"], "customers_served": 74, "hp_share_base": 0.12, "hp_share_forecast": 0.2, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-ITT-128 School Rd pole

- Why flagged: rule 4: Chart signal: a few outliers; the load pattern may have changed and capability is not calculated until it is explained
- Chart signal: beyond_3_sigma on 2026-10-13 (value 61.5)
- Chart signal: moving_range_beyond_ucl on 2026-10-13 (value 15.2)
- Chart signal: moving_range_beyond_ucl on 2026-10-14 (value 17.6)
- Forecast assumptions: {"reason_not_projected": "load pattern signal"}
- Disposition: none recorded yet

### T-ITT-130 Hill Rd pole

- Why flagged: rule 4: Chart signal: a few outliers; the load pattern may have changed and capability is not calculated until it is explained
- Chart signal: beyond_3_sigma on 2026-10-13 (value 41.0)
- Chart signal: moving_range_beyond_ucl on 2026-10-13 (value 13.8)
- Chart signal: moving_range_beyond_ucl on 2026-10-14 (value 12.2)
- Forecast assumptions: {"reason_not_projected": "load pattern signal"}
- Disposition: none recorded yet

### T-ITT-137 Hollow Rd pole

- Why flagged: rule 4: Chart signal: a few outliers; the load pattern may have changed and capability is not calculated until it is explained
- Chart signal: beyond_3_sigma on 2026-10-13 (value 30.8)
- Chart signal: moving_range_beyond_ucl on 2026-10-13 (value 11.0)
- Chart signal: moving_range_beyond_ucl on 2026-10-14 (value 7.8)
- Forecast assumptions: {"reason_not_projected": "load pattern signal"}
- Disposition: none recorded yet

### T-ITT-158 Valley Rd pad

- Why flagged: rule 2: Sustained shift this period: a run rule fired (8 in a row on one side of the centre line or 2 of 3 beyond 2 sigma)
- Chart signal: two_of_three_beyond_2_sigma on 2026-10-12 (value 234.0)
- Chart signal: two_of_three_beyond_2_sigma on 2026-10-13 (value 230.4)
- Chart signal: eight_in_a_row_one_side on 2026-10-12 (value 234.0)
- Forecast assumptions: {"reason_not_projected": "load pattern signal"}
- Disposition: none recorded yet

### T-ITT-160 Hanshaw Rd pad

- Why flagged: rule 4: Chart signal: a few outliers; the load pattern may have changed and capability is not calculated until it is explained
- Chart signal: beyond_3_sigma on 2026-10-13 (value 82.0)
- Chart signal: moving_range_beyond_ucl on 2026-10-14 (value 21.5)
- Forecast assumptions: {"reason_not_projected": "load pattern signal"}
- Disposition: none recorded yet

### T-ITT-161 Hanshaw Rd pad

- Why flagged: rule 4: Chart signal: a few outliers; the load pattern may have changed and capability is not calculated until it is explained
- Chart signal: beyond_3_sigma on 2026-10-13 (value 136.9)
- Chart signal: moving_range_beyond_ucl on 2026-10-13 (value 35.6)
- Chart signal: moving_range_beyond_ucl on 2026-10-14 (value 39.3)
- Forecast assumptions: {"reason_not_projected": "load pattern signal"}
- Disposition: none recorded yet

### T-ITT-165 Church St pole

- Why flagged: rule 9: Low Cpk against the rated maximum (playbook threshold 1.33)
- Forecast assumptions: {"added_kw": 2.8800000000000003, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "ITH-T", "area_name": "Town of Ithaca", "allocation_method": "declared_primary_area", "allocation_flagged": true, "located_areas": ["ITH-T", "DAN", "NEW"], "customers_served": 15, "hp_share_base": 0.12, "hp_share_forecast": 0.2, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-ITT-167 Maple Ave pad

- Why flagged: rule 10: Uncertain Cpk: the lower 95% confidence bound is below 1.33
- Forecast assumptions: {"added_kw": 5.952000000000001, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "ITH-T", "area_name": "Town of Ithaca", "allocation_method": "declared_primary_area", "allocation_flagged": true, "located_areas": ["ITH-T", "LAN"], "customers_served": 31, "hp_share_base": 0.12, "hp_share_forecast": 0.2, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-ITT-170 Valley Rd pad

- Why flagged: rule 4: Chart signal: a few outliers; the load pattern may have changed and capability is not calculated until it is explained
- Chart signal: beyond_3_sigma on 2026-10-13 (value 82.0)
- Chart signal: moving_range_beyond_ucl on 2026-10-13 (value 27.5)
- Chart signal: moving_range_beyond_ucl on 2026-10-14 (value 25.8)
- Forecast assumptions: {"reason_not_projected": "load pattern signal"}
- Disposition: none recorded yet

### T-ITT-176 Brook Rd pole

- Why flagged: rule 4: Chart signal: a few outliers; the load pattern may have changed and capability is not calculated until it is explained
- Chart signal: beyond_3_sigma on 2026-10-13 (value 61.5)
- Chart signal: moving_range_beyond_ucl on 2026-10-13 (value 13.6)
- Chart signal: moving_range_beyond_ucl on 2026-10-14 (value 16.8)
- Forecast assumptions: {"reason_not_projected": "load pattern signal"}
- Disposition: none recorded yet

### T-LAN-005 Triphammer Rd pad

- Why flagged: rule 10: Uncertain Cpk: the lower 95% confidence bound is below 1.33
- Forecast assumptions: {"added_kw": 14.400000000000002, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "LAN", "area_name": "Town of Lansing", "allocation_method": "declared_primary_area", "allocation_flagged": false, "located_areas": ["LAN"], "customers_served": 75, "hp_share_base": 0.12, "hp_share_forecast": 0.2, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-LAN-103 Falls Rd pole

- Why flagged: rule 9: Low Cpk against the rated maximum (playbook threshold 1.33)
- Forecast assumptions: {"added_kw": 5.760000000000001, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "LAN", "area_name": "Town of Lansing", "allocation_method": "declared_primary_area", "allocation_flagged": false, "located_areas": ["LAN"], "customers_served": 30, "hp_share_base": 0.12, "hp_share_forecast": 0.2, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-LAN-110 Station Rd pole

- Why flagged: rule 9: Low Cpk against the rated maximum (playbook threshold 1.33)
- Forecast assumptions: {"added_kw": 2.112, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "LAN", "area_name": "Town of Lansing", "allocation_method": "declared_primary_area", "allocation_flagged": false, "located_areas": ["LAN"], "customers_served": 11, "hp_share_base": 0.12, "hp_share_forecast": 0.2, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-LAN-111 Station Rd pole

- Why flagged: rule 3: Repeated outliers this period (3 or more days beyond 3 sigma or with a moving-range spike)
- Chart signal: beyond_3_sigma on 2026-10-10 (value 61.5)
- Chart signal: beyond_3_sigma on 2026-10-12 (value 28.5)
- Chart signal: beyond_3_sigma on 2026-10-14 (value 61.5)
- Chart signal: moving_range_beyond_ucl on 2026-10-10 (value 12.8)
- Chart signal: moving_range_beyond_ucl on 2026-10-11 (value 15.1)
- Chart signal: moving_range_beyond_ucl on 2026-10-12 (value 17.9)
- Chart signal: moving_range_beyond_ucl on 2026-10-13 (value 14.1)
- Chart signal: moving_range_beyond_ucl on 2026-10-14 (value 18.9)
- Chart signal: moving_range_beyond_ucl on 2026-10-15 (value 14.3)
- Forecast assumptions: {"reason_not_projected": "load pattern signal"}
- Disposition: none recorded yet

### T-LAN-120 Hanshaw Rd pole

- Why flagged: rule 4: Chart signal: a few outliers; the load pattern may have changed and capability is not calculated until it is explained
- Chart signal: beyond_3_sigma on 2026-10-13 (value 41.0)
- Chart signal: moving_range_beyond_ucl on 2026-10-13 (value 7.9)
- Chart signal: moving_range_beyond_ucl on 2026-10-14 (value 9.7)
- Forecast assumptions: {"reason_not_projected": "load pattern signal"}
- Disposition: none recorded yet

### T-LAN-137 Hollow Rd pole

- Why flagged: rule 2: Sustained shift this period: a run rule fired (8 in a row on one side of the centre line or 2 of 3 beyond 2 sigma)
- Chart signal: two_of_three_beyond_2_sigma on 2026-10-07 (value 27.3)
- Chart signal: two_of_three_beyond_2_sigma on 2026-10-08 (value 26.1)
- Chart signal: two_of_three_beyond_2_sigma on 2026-10-11 (value 27.2)
- Chart signal: two_of_three_beyond_2_sigma on 2026-10-12 (value 27.0)
- Chart signal: two_of_three_beyond_2_sigma on 2026-10-13 (value 25.6)
- Chart signal: eight_in_a_row_one_side on 2026-10-13 (value 25.6)
- Forecast assumptions: {"reason_not_projected": "load pattern signal"}
- Disposition: none recorded yet

### T-LAN-143 Valley Rd pole

- Why flagged: rule 4: Chart signal: a few outliers; the load pattern may have changed and capability is not calculated until it is explained
- Chart signal: beyond_3_sigma on 2026-10-13 (value 41.0)
- Chart signal: moving_range_beyond_ucl on 2026-10-13 (value 10.6)
- Chart signal: moving_range_beyond_ucl on 2026-10-14 (value 10.4)
- Forecast assumptions: {"reason_not_projected": "load pattern signal"}
- Disposition: none recorded yet

### T-LAN-154 Lake Rd pad

- Why flagged: rule 5: Not enough stable history to judge the load pattern; a person decides
- Forecast assumptions: {"reason_not_projected": "load pattern insufficient_history"}
- Disposition: none recorded yet

### T-LAN-158 Pine Tree Rd pad

- Why flagged: rule 4: Chart signal: a few outliers; the load pattern may have changed and capability is not calculated until it is explained
- Chart signal: beyond_3_sigma on 2026-10-13 (value 82.0)
- Chart signal: moving_range_beyond_ucl on 2026-10-13 (value 23.0)
- Chart signal: moving_range_beyond_ucl on 2026-10-14 (value 17.4)
- Forecast assumptions: {"reason_not_projected": "load pattern signal"}
- Disposition: none recorded yet

### T-NEW-105 Ridge Rd pad

- Why flagged: rule 5: Not enough stable history to judge the load pattern; a person decides
- Forecast assumptions: {"reason_not_projected": "load pattern insufficient_history"}
- Disposition: none recorded yet

### T-NEW-109 Creek Rd pad

- Why flagged: rule 9: Low Cpk against the rated maximum (playbook threshold 1.33)
- Forecast assumptions: {"added_kw": 14.400000000000002, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "NEW", "area_name": "Town of Newfield", "allocation_method": "declared_primary_area", "allocation_flagged": true, "located_areas": ["ITH-T", "ENF", "NEW"], "customers_served": 75, "hp_share_base": 0.12, "hp_share_forecast": 0.2, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-NEW-110 Creek Rd pole

- Why flagged: rule 10: Uncertain Cpk: the lower 95% confidence bound is below 1.33
- Forecast assumptions: {"added_kw": 1.344, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "NEW", "area_name": "Town of Newfield", "allocation_method": "declared_primary_area", "allocation_flagged": true, "located_areas": ["ITH-T", "DAN", "NEW"], "customers_served": 7, "hp_share_base": 0.12, "hp_share_forecast": 0.2, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

### T-NEW-112 Valley Rd pad

- Why flagged: rule 4: Chart signal: a few outliers; the load pattern may have changed and capability is not calculated until it is explained
- Chart signal: beyond_3_sigma on 2026-10-13 (value 82.0)
- Chart signal: moving_range_beyond_ucl on 2026-10-13 (value 24.4)
- Chart signal: moving_range_beyond_ucl on 2026-10-14 (value 18.2)
- Forecast assumptions: {"reason_not_projected": "load pattern signal"}
- Disposition: none recorded yet

### T-TRU-012 Main St pad

- Why flagged: rule 3: Repeated outliers this period (3 or more days beyond 3 sigma or with a moving-range spike)
- Chart signal: beyond_3_sigma on 2026-10-10 (value 82.0)
- Chart signal: beyond_3_sigma on 2026-10-12 (value 38.0)
- Chart signal: beyond_3_sigma on 2026-10-14 (value 82.0)
- Chart signal: moving_range_beyond_ucl on 2026-10-10 (value 22.0)
- Chart signal: moving_range_beyond_ucl on 2026-10-11 (value 24.0)
- Chart signal: moving_range_beyond_ucl on 2026-10-12 (value 20.0)
- Chart signal: moving_range_beyond_ucl on 2026-10-13 (value 20.2)
- Chart signal: moving_range_beyond_ucl on 2026-10-14 (value 23.8)
- Chart signal: moving_range_beyond_ucl on 2026-10-15 (value 20.9)
- Forecast assumptions: {"reason_not_projected": "load pattern signal"}
- Disposition: none recorded yet

### T-TRU-103 Ridge Rd pad

- Why flagged: rule 4: Chart signal: a few outliers; the load pattern may have changed and capability is not calculated until it is explained
- Chart signal: beyond_3_sigma on 2026-10-13 (value 82.0)
- Chart signal: moving_range_beyond_ucl on 2026-10-13 (value 27.3)
- Chart signal: moving_range_beyond_ucl on 2026-10-14 (value 24.6)
- Forecast assumptions: {"reason_not_projected": "load pattern signal"}
- Disposition: none recorded yet

### T-ULY-007 Jacksonville Rd pole (new)

- Why flagged: rule 5: Not enough stable history to judge the load pattern; a person decides
- Forecast assumptions: {"reason_not_projected": "load pattern insufficient_history"}
- Disposition: none recorded yet

### T-ULY-107 Brook Rd pad

- Why flagged: rule 3: Repeated outliers this period (3 or more days beyond 3 sigma or with a moving-range spike)
- Chart signal: beyond_3_sigma on 2026-10-10 (value 82.0)
- Chart signal: beyond_3_sigma on 2026-10-12 (value 38.0)
- Chart signal: beyond_3_sigma on 2026-10-14 (value 82.0)
- Chart signal: moving_range_beyond_ucl on 2026-10-10 (value 20.9)
- Chart signal: moving_range_beyond_ucl on 2026-10-11 (value 20.9)
- Chart signal: moving_range_beyond_ucl on 2026-10-12 (value 23.1)
- Chart signal: moving_range_beyond_ucl on 2026-10-13 (value 21.2)
- Chart signal: moving_range_beyond_ucl on 2026-10-14 (value 22.8)
- Chart signal: moving_range_beyond_ucl on 2026-10-15 (value 18.4)
- Forecast assumptions: {"reason_not_projected": "load pattern signal"}
- Disposition: none recorded yet

### T-ULY-110 Main St pad

- Why flagged: rule 5: Not enough stable history to judge the load pattern; a person decides
- Forecast assumptions: {"reason_not_projected": "load pattern insufficient_history"}
- Disposition: none recorded yet

### T-ULY-113 Cemetery Rd pole

- Why flagged: rule 4: Chart signal: a few outliers; the load pattern may have changed and capability is not calculated until it is explained
- Chart signal: beyond_3_sigma on 2026-10-13 (value 30.8)
- Chart signal: moving_range_beyond_ucl on 2026-10-13 (value 6.5)
- Chart signal: moving_range_beyond_ucl on 2026-10-14 (value 7.9)
- Forecast assumptions: {"reason_not_projected": "load pattern signal"}
- Disposition: none recorded yet

### T-ULY-114 Lake Rd pole

- Why flagged: rule 4: Chart signal: a few outliers; the load pattern may have changed and capability is not calculated until it is explained
- Chart signal: beyond_3_sigma on 2026-10-13 (value 30.8)
- Chart signal: moving_range_beyond_ucl on 2026-10-13 (value 9.1)
- Chart signal: moving_range_beyond_ucl on 2026-10-14 (value 7.4)
- Forecast assumptions: {"reason_not_projected": "load pattern signal"}
- Disposition: none recorded yet

### T-ULY-116 Ridge Rd pad

- Why flagged: rule 10: Uncertain Cpk: the lower 95% confidence bound is below 1.33
- Forecast assumptions: {"added_kw": 10.368000000000002, "power_factor": 0.95, "unit_note": "kW converted to kVA using power factor 0.95", "forecast_version": "TC-HP-2026-v1", "horizon": "2030 winter peak", "area_id": "ULY", "area_name": "Town of Ulysses", "allocation_method": "declared_primary_area", "allocation_flagged": true, "located_areas": ["ENF", "ULY"], "customers_served": 54, "hp_share_base": 0.12, "hp_share_forecast": 0.2, "kw_per_heat_pump": 2.4, "formula": "projected_peak = period_peak + customers x (hp_share_forecast - hp_share_base) x kw_per_heat_pump / power_factor"}
- Disposition: none recorded yet

---
This report was produced by fixed rules (no AI). It does not change any equipment or operating setting.