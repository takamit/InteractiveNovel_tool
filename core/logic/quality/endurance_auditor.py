from __future__ import annotations

from dataclasses import dataclass
from statistics import mean, pstdev
from typing import Any

from core.logic.runtime.world_state import WorldState


@dataclass(slots=True)
class EnduranceAuditor:
    """Build a long-run stability report from multiple per-turn snapshots."""

    def build_report(self, snapshots: list[dict[str, Any]], state: WorldState) -> dict[str, Any]:
        if not snapshots:
            return {
                'turn_count': 0,
                'stability_score': 0.0,
                'alerts': ['no snapshots available'],
                'volatility': {},
                'recent_turn_traces': list(state.turn_traces[-3:]),
            }

        world_tension_series = [float(item['world_tension']) for item in snapshots]
        avg_stress_series = [float(item['avg_stress']) for item in snapshots]
        max_stress_series = [float(item['max_stress']) for item in snapshots]
        max_heat_series = [float(item['max_location_heat']) for item in snapshots]
        max_suspicion_series = [float(item['max_suspicion']) for item in snapshots]
        secret_count_series = [int(item['revealed_secret_count']) for item in snapshots]

        volatility = {
            'world_tension_stddev': round(pstdev(world_tension_series) if len(world_tension_series) > 1 else 0.0, 4),
            'avg_stress_stddev': round(pstdev(avg_stress_series) if len(avg_stress_series) > 1 else 0.0, 4),
            'max_heat_stddev': round(pstdev(max_heat_series) if len(max_heat_series) > 1 else 0.0, 4),
            'max_suspicion_stddev': round(pstdev(max_suspicion_series) if len(max_suspicion_series) > 1 else 0.0, 4),
        }

        alerts: list[str] = []
        if max(max_stress_series) >= 95.0:
            alerts.append('max stress reached critical range')
        if max(world_tension_series) >= 92.0:
            alerts.append('world tension reached critical range')
        if volatility['world_tension_stddev'] >= 12.0:
            alerts.append('world tension is too volatile')
        if volatility['avg_stress_stddev'] >= 10.0:
            alerts.append('stress curve is too volatile')
        if secret_count_series[-1] == 0 and len(snapshots) >= 15:
            alerts.append('no secrets surfaced across endurance run')
        if max(max_heat_series) >= 90.0:
            alerts.append('location heat accumulated too aggressively')

        last_snapshot = snapshots[-1]
        pressure_peaks = sorted(
            (
                {'turn': item['turn'], 'world_tension': round(float(item['world_tension']), 4), 'max_stress': round(float(item['max_stress']), 4)}
                for item in snapshots
            ),
            key=lambda row: (row['world_tension'], row['max_stress']),
            reverse=True,
        )[:5]

        score = 100.0
        score -= len(alerts) * 8.5
        score -= min(volatility['world_tension_stddev'] * 0.9, 15.0)
        score -= min(volatility['avg_stress_stddev'] * 0.8, 12.0)
        score -= min(mean(max_suspicion_series) / 9.0, 10.0)
        score -= min(mean(max_heat_series) / 11.0, 9.0)
        score = round(max(0.0, min(100.0, score)), 2)

        recommendations: list[str] = []
        if volatility['world_tension_stddev'] >= 12.0:
            recommendations.append('reduce world fallout coefficients or strengthen passive cooldown')
        if max(max_suspicion_series) >= 88.0:
            recommendations.append('soften suspicion gain on confront and rumor spillover')
        if max(max_heat_series) >= 88.0:
            recommendations.append('increase location heat decay per turn')
        if max(max_stress_series) >= 90.0:
            recommendations.append('raise recovery impact for support and seek_help')
        if secret_count_series[-1] == 0 and len(snapshots) >= 15:
            recommendations.append('ease secret reveal pressure in private scenes')

        return {
            'turn_count': len(snapshots),
            'stability_score': score,
            'alerts': alerts,
            'recommendations': recommendations,
            'volatility': volatility,
            'last_snapshot': last_snapshot,
            'pressure_peaks': pressure_peaks,
            'recent_turn_traces': list(state.turn_traces[-5:]),
        }
