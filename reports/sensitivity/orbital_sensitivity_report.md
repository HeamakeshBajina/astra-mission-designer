# ASTRA Orbital Sensitivity Analysis

**Method:** One-at-a-time parametric sensitivity analysis

Rank by maximum absolute relative metric change across the supplied perturbations.

## Baseline metrics

| Metric | Baseline value |
|---|---:|
| circular_speed_m_s | 7672.598648 |
| hohmann_total_delta_v_m_s | 217.0153084 |
| hohmann_transfer_time_s | 2896.167055 |
| orbital_period_s | 5544.855096 |

## Sensitivity rankings

### circular_speed_m_s

| Rank | Parameter | Maximum absolute relative change (%) |
|---:|---|---:|
| 1 | initial_radius | 2.5978352 |
| 2 | earth_mu | 2.5320566 |
| 3 | final_radius | 0 |

### hohmann_total_delta_v_m_s

| Rank | Parameter | Maximum absolute relative change (%) |
|---:|---|---:|
| 1 | initial_radius | 91.725805 |
| 2 | final_radius | 89.227799 |
| 3 | earth_mu | 2.5320566 |

### hohmann_transfer_time_s

| Rank | Parameter | Maximum absolute relative change (%) |
|---:|---|---:|
| 1 | final_radius | 3.8822849 |
| 2 | initial_radius | 3.6644347 |
| 3 | earth_mu | 2.5978352 |

### orbital_period_s

| Rank | Parameter | Maximum absolute relative change (%) |
|---:|---|---:|
| 1 | initial_radius | 7.592983 |
| 2 | earth_mu | 2.5978352 |
| 3 | final_radius | 0 |

## Perturbation results

| Metric | Parameter | Perturbation (%) | Baseline | Perturbed | Absolute change | Relative change (%) |
|---|---|---:|---:|---:|---:|---:|
| circular_speed_m_s | earth_mu | -5 | 7672.598648 | 7478.324112 | -194.2745368 | -2.5320566 |
| circular_speed_m_s | earth_mu | -1 | 7672.598648 | 7634.139265 | -38.45938328 | -0.50125629 |
| circular_speed_m_s | earth_mu | 1 | 7672.598648 | 7710.866211 | 38.26756232 | 0.49875621 |
| circular_speed_m_s | earth_mu | 5 | 7672.598648 | 7862.07406 | 189.4754113 | 2.4695077 |
| circular_speed_m_s | final_radius | -5 | 7672.598648 | 7672.598648 | 0 | 0 |
| circular_speed_m_s | final_radius | -1 | 7672.598648 | 7672.598648 | 0 | 0 |
| circular_speed_m_s | final_radius | 1 | 7672.598648 | 7672.598648 | 0 | 0 |
| circular_speed_m_s | final_radius | 5 | 7672.598648 | 7672.598648 | 0 | 0 |
| circular_speed_m_s | initial_radius | -5 | 7672.598648 | 7871.920117 | 199.3214691 | 2.5978352 |
| circular_speed_m_s | initial_radius | -1 | 7672.598648 | 7711.251783 | 38.65313455 | 0.50378153 |
| circular_speed_m_s | initial_radius | 1 | 7672.598648 | 7634.521001 | -38.07764769 | -0.49628098 |
| circular_speed_m_s | initial_radius | 5 | 7672.598648 | 7487.689581 | -184.9090677 | -2.4099927 |
| hohmann_total_delta_v_m_s | earth_mu | -5 | 217.0153084 | 211.5203581 | -5.494950335 | -2.5320566 |
| hohmann_total_delta_v_m_s | earth_mu | -1 | 217.0153084 | 215.9275055 | -1.087802882 | -0.50125629 |
| hohmann_total_delta_v_m_s | earth_mu | 1 | 217.0153084 | 218.0976857 | 1.08237733 | 0.49875621 |
| hohmann_total_delta_v_m_s | earth_mu | 5 | 217.0153084 | 222.3745181 | 5.359209664 | 2.4695077 |
| hohmann_total_delta_v_m_s | final_radius | -5 | 217.0153084 | 23.37732445 | -193.637984 | -89.227799 |
| hohmann_total_delta_v_m_s | final_radius | -1 | 217.0153084 | 179.4752173 | -37.54009114 | -17.298361 |
| hohmann_total_delta_v_m_s | final_radius | 1 | 217.0153084 | 253.988417 | 36.97310862 | 17.037097 |
| hohmann_total_delta_v_m_s | final_radius | 5 | 217.0153084 | 396.4586135 | 179.4433051 | 82.686934 |
| hohmann_total_delta_v_m_s | initial_radius | -5 | 217.0153084 | 416.0743466 | 199.0590382 | 91.725805 |
| hohmann_total_delta_v_m_s | initial_radius | -1 | 217.0153084 | 255.6404477 | 38.62513933 | 17.798348 |
| hohmann_total_delta_v_m_s | initial_radius | 1 | 217.0153084 | 178.9571626 | -38.05814583 | -17.537079 |
| hohmann_total_delta_v_m_s | initial_radius | 5 | 217.0153084 | 32.15077064 | -184.8645378 | -85.185022 |
| hohmann_transfer_time_s | earth_mu | -5 | 2896.167055 | 2971.404702 | 75.23764745 | 2.5978352 |
| hohmann_transfer_time_s | earth_mu | -1 | 2896.167055 | 2910.757409 | 14.59035458 | 0.50378153 |
| hohmann_transfer_time_s | earth_mu | 1 | 2896.167055 | 2881.793929 | -14.37312621 | -0.49628098 |
| hohmann_transfer_time_s | earth_mu | 5 | 2896.167055 | 2826.36964 | -69.79741475 | -2.4099927 |
| hohmann_transfer_time_s | final_radius | -5 | 2896.167055 | 2785.166251 | -111.0008035 | -3.8326796 |
| hohmann_transfer_time_s | final_radius | -1 | 2896.167055 | 2873.851369 | -22.31568535 | -0.7705248 |
| hohmann_transfer_time_s | final_radius | 1 | 2896.167055 | 2918.540204 | 22.37314923 | 0.77250893 |
| hohmann_transfer_time_s | final_radius | 5 | 2896.167055 | 3008.604512 | 112.4374573 | 3.8822849 |
| hohmann_transfer_time_s | initial_radius | -5 | 2896.167055 | 2791.31975 | -104.8473053 | -3.6202092 |
| hohmann_transfer_time_s | initial_radius | -1 | 2896.167055 | 2875.094628 | -21.07242719 | -0.72759709 |
| hohmann_transfer_time_s | initial_radius | 1 | 2896.167055 | 2917.290714 | 21.12365915 | 0.72936605 |
| hohmann_transfer_time_s | initial_radius | 5 | 2896.167055 | 3002.295204 | 106.1281496 | 3.6644347 |
| orbital_period_s | earth_mu | -5 | 5544.855096 | 5688.901294 | 144.0461979 | 2.5978352 |
| orbital_period_s | earth_mu | -1 | 5544.855096 | 5572.789052 | 27.93395561 | 0.50378153 |
| orbital_period_s | earth_mu | 1 | 5544.855096 | 5517.337035 | -27.51806115 | -0.49628098 |
| orbital_period_s | earth_mu | 5 | 5544.855096 | 5411.224493 | -133.6306033 | -2.4099927 |
| orbital_period_s | final_radius | -5 | 5544.855096 | 5544.855096 | 0 | 0 |
| orbital_period_s | final_radius | -1 | 5544.855096 | 5544.855096 | 0 | 0 |
| orbital_period_s | final_radius | 1 | 5544.855096 | 5544.855096 | 0 | 0 |
| orbital_period_s | final_radius | 5 | 5544.855096 | 5544.855096 | 0 | 0 |
| orbital_period_s | initial_radius | -5 | 5544.855096 | 5134.233418 | -410.6216782 | -7.4054537 |
| orbital_period_s | initial_radius | -1 | 5544.855096 | 5461.890549 | -82.96454651 | -1.4962437 |
| orbital_period_s | initial_radius | 1 | 5544.855096 | 5628.235509 | 83.38041325 | 1.5037438 |
| orbital_period_s | initial_radius | 5 | 5544.855096 | 5965.875003 | 421.0199072 | 7.592983 |

## Limitations

- Rankings describe only the supplied perturbation cases.
- This is not probabilistic uncertainty propagation.
- Rankings depend on the baseline and perturbation range.
- Sensitivity alone does not establish engineering risk.
