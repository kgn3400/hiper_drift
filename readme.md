<!-- markdownlint-disable MD041 -->
![GitHub release (latest by date)](https://img.shields.io/github/v/release/kgn3400/hiper_drift)
![GitHub all releases](https://img.shields.io/github/downloads/kgn3400/hiper_drift/total)
![GitHub last commit](https://img.shields.io/github/last-commit/kgn3400/hiper_drift)
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/kgn3400/hiper_drift)
[![Validate% with hassfest](https://github.com/kgn3400/hiper_drift/workflows/Validate%20with%20hassfest/badge.svg)](https://github.com/kgn3400/hiper_drift/actions/workflows/hassfest.yaml)

<img align="left" width="80" height="80" src="https://kgn3400.github.io/hiper_drift/assets/icon@2x.png" alt="App icon">

# Hiper drift

<br/>

Hiper drift integrationen giver dig mulighed for at modtage advarsler om den danske internetudbyder Hipers driftsstatus.

## Installation

For at installere TrafikmeHiper drift integrationen, søg efter `Hiper drift` i HACS og download.
Eller klik på
[![My Home Assistant](https://img.shields.io/badge/Home%20Assistant-%2341BDF5.svg?style=flat&logo=home-assistant&label=Add%20to%20HACS)](https://my.home-assistant.io/redirect/hacs_repository/?owner=kgn3400&repository=hiper_drift&category=integration)

Tilføj Hiper drift integrationen til Home Assistant.
[![Åbn Home Assistant og begynd at opsætte en ny integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=hiper_drift)

## Konfiguration

Konfiguration opsættes via brugergrænsefladen i Home Assistant.

## Sensorer

Der to binary sensorer er tilgængelige:

'binary_sensor.hiper_drift_generel' - Generelle driftsstatus

```Python
{{ state_attr('binary_sensor.hiper_drift_generel','markdown') }}
```

'binary_sensor.hiper_drift_regional' - Regionale driftsstatus

```Python
{{ state_attr('binary_sensor.hiper_drift_regional','markdown') }}
```

## Aktioner

Available actions: __Opdater__ og __Marker som læst__

### Support

Hvis du synes godt om denne integration, eller finder den brugbar, må du meget gerne give den en ⭐️ på GitHub 👍 Det vil blive værdsat!
