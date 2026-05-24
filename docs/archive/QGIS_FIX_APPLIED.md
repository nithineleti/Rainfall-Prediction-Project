# QGIS Script Updated - API Fix Applied

## Issue
The QGIS 3.x API changed how `QgsZonalStatistics` accepts parameters.

## Fix Applied
Updated `qgis_characterize_watersheds.py` to use:
- `QgsZonalStatistics.Mean` instead of numeric codes
- `QgsZonalStatistics.StDev` instead of `32`
- `QgsZonalStatistics.Max` instead of `128`
- `QgsZonalStatistics.Min` instead of `64`

## Re-run Now

In QGIS Python Console, run again:

```python
exec(open('G:/PROJECTS/watershed-up/qgis_characterize_watersheds.py').read())
```

The script should now complete successfully!
