# xtide Module - Global Tide Predictions

This module provides global tide prediction capabilities using the [tidepredict](https://github.com/windcrusader/tidepredict) library, which uses the University of Hawaii's Research Quality Dataset for worldwide tide station coverage.

## Features

- Global tide predictions (not limited to US locations like NOAA)
- Offline predictions once station data is initialized
- Automatic selection of nearest tide station
- Compatible with existing tide command interface

## Installation

1. Install tidepredict library:
this takes about 3-500MB of disk

```bash
pip install tidepredict
```
note: if you see warning about system packages the override for debian OS to install it anyway is..

```bash
pip install tidepredict --break-system-packages
```

2. Enable in `config.ini`:
```ini
[location]
useTidePredict = True
```

## First-Time Setup

On first use, tidepredict needs to download station data from the University of Hawaii FTP server. This requires internet access and happens automatically when you:

1. Run the tide command for the first time with `useTidePredict = True`
2. Or manually initialize with:
```bash
python3 -m tidepredict -l <location> -genharm
```

The station data is cached locally in `~/.tidepredict/` for offline use afterward.

No other downloads will happen automatically, its offline

## Usage

Once enabled, the existing `tide` command will automatically use tidepredict for global locations:

```
tide
```

The module will:
1. Find the nearest tide station to your GPS coordinates
2. Load harmonic constituents for that station
3. Calculate tide predictions for today
4. Format output compatible with mesh display

## Configuration

### config.ini Options

```ini
[location]
# Enable global tide predictions using tidepredict
useTidePredict = True

# Standard location settings still apply
lat = 48.50
lon = -123.0
useMetric = False
```

## Fallback Behavior

If tidepredict is not available or encounters errors, the module will automatically fall back to the NOAA API for US locations.

## Limitations

- First-time setup requires internet access to download station database
- Station coverage depends on University of Hawaii's dataset
- Predictions may be less accurate for locations far from tide stations

## Troubleshooting

### "Station database not initialized" error

This means the station data hasn't been downloaded yet. Ensure internet access and:

```bash
# Test station download
python3 -m tidepredict -l Sydney

# Or manually run initialization
python3 -c "from tidepredict import process_station_list; process_station_list.create_station_dataframe()"
```

### "No tide station found nearby"

The module couldn't find a nearby station. This may happen if:
- You're in a location without nearby tide monitoring stations
- The station database hasn't been initialized
- Network issues prevented loading the station list

Tide Station Map 
[https://uhslc.soest.hawaii.edu/network/](https://uhslc.soest.hawaii.edu/network/)
- click on Tide Guages
- Find yourself on the map
- Locate the closest Gauge and its name (typically the city name)

To manually download data for the station first location the needed station id
- `python -m tidepredict -l "Port Angeles"` finds a station
- `python -m tidepredict -l "Port Angeles" -genharm` downloads that datafile



## Data Source

Tide predictions are based on harmonic analysis of historical tide data from:
- University of Hawaii Sea Level Center (UHSLC)
- Research Quality Dataset
- Global coverage with 600+ stations

## References

- [tidepredict GitHub](https://github.com/windcrusader/tidepredict)
- [UHSLC Data](https://uhslc.soest.hawaii.edu/)
- [pytides](https://github.com/sam-cox/pytides) - Underlying tide calculation library
