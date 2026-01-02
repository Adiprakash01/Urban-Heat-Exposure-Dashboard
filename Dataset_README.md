Dataset_README.md

## Uber heat exposure analysis in global cities

1. Dataset Title  
Daily Near-Surface Air Temperature Time-Series Dataset for Global Urban Heat Exposure Analysis

2. Dataset Description  
This dataset contains daily near-surface air temperature observations for selected global cities, namely Mumbai, Dubai, Singapore, London, New York, and Sydney. The dataset has been prepared to support comparative urban heat exposure analysis using geospatial visualization and time-series analytical techniques.

Temperature data were programmatically retrieved from the NASA POWER (Prediction of Worldwide Energy Resources) API, which provides open-access climate data derived from satellite observations and numerical reanalysis models. The dataset enables cross-city comparison of urban temperature trends across diverse climatic regimes.

3. Geographic Coverage  

Cities Covered:
- Mumbai, India  
- Dubai, United Arab Emirates  
- Singapore  
- London, United Kingdom  
- New York, United States  
- Sydney, Australia  

Each city is represented using point-based geographic coordinates (latitude and longitude).

4. Temporal Coverage  

- Start Date: 01 January 2024  
- End Date: 31 December 2025  
- Temporal Resolution: Daily  

5. Data Source  

- Source: NASA POWER Project (Prediction of Worldwide Energy Resources)  
- Access Method: Public REST API  
- Climate Variable Used:  
  - T2M – Near-surface air temperature (measured in °C)

Official website:  
https://power.larc.nasa.gov/

6. Data Type and Format  

- Geospatial Data Type: Point-based vector data  
- Coordinate Reference System (CRS): EPSG:4326 (WGS 84)  
- File Format: CSV (Comma-Separated Values)  

7. Attribute Description  

 Column Name  Description 
Area : Name of the city 
 Latitude: Latitude of the city 
 Longitude: Longitude of the city 
 Date: Observation date (YYYY-MM-DD) 
 Temperature_C: Daily mean near-surface air temperature (°C) 

8. Data Cleaning and Processing  

The dataset was preprocessed prior to analysis. Missing or invalid temperature values returned by the NASA POWER API (encoded as -999) were identified and removed. Date fields were validated and converted into a standardized daily datetime format. Records were sorted by city and date to ensure suitability for time-series analysis.

9. Intended Use  

This dataset is intended for academic and analytical purposes, including:
- Comparative urban heat exposure studies  
- Geospatial analytics coursework  
- Time-series analysis of urban climate patterns  
- Climate variability assessment across cities  

10. Limitations  

The dataset is derived from satellite-based reanalysis models and does not represent direct ground-station measurements. Due to the spatial resolution of reanalysis data, fine-scale urban microclimate variations may not be fully captured. The dataset represents near-surface air temperature rather than land surface temperature (LST).

11. License and Usage  

The dataset is based on open-access climate data provided by the NASA POWER project and is intended strictly for academic and non-commercial use.

12. Prepared By  

Prepared as part of a Geospatial Analytics Internal Assessment  
Narsee Monjee College of Commerce and Economics  
University of Mumbai
