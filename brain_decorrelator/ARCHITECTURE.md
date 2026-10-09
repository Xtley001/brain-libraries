# Architecture — brain-decorrelator

```mermaid
flowchart LR
    subgraph Core[brain_decorrelator]
        Engine[DecorrelationEngine]
        Plugin[AxisPlugin ABC]
        Registry[_AXIS_REGISTRY]
    end
    subgraph BuiltIn[axes/universal.py]
        V[VelocityShiftAxis]
        C[CalendarSpreadAxis]
        VR[VolumeRegimeAxis]
        Vol[VolatilityRegimeAxis]
        N[NeutralizationRotationAxis]
        R[CrossSectionalRankAxis]
    end
    subgraph Domain[brain_options / brain_sentiment / etc.]
        DO[Domain Axes]
    end
    V & C & VR & Vol & N & R -->|@register_axis| Registry
    DO -->|@register_axis| Registry
    Engine --> Registry
```

The `DecorrelationEngine` is stateless and calls plugins in registration order.
Duplicate variants are eliminated by SHA-256 hash.
