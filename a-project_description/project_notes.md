## Context: 

Adoption HP+TES systems for residential applications is limited by lack of easily adoptable control systems coordinating the use of the HP and the TES.

Installations of TES systems require contractors to develop controls dictating when the HP operates in response to the SoC of the TES. But this is difficult to do for typical contractors.

MPC is a possibility but not being adopted, perhaps due to complexity and lack of adaptability.

## This project:

Create and test a simplified price-responsive control algorithm that coordinates the HP and TES. Share as an open source tool.

The controller will use on-site data measurements and machine learning algorithms to learn the behavior of the system, facilitating control without detailed simulation models. 

The testing will be simulations for both California and New England contexts, using simulation models developed in previous projects at LBNL. In the future expect testing the algorithms in the lab and field.

## forecaster.zip

LBNL's library of ML tools
- fcLib.py contains the library of ML forecaster tools. 
- fcSelector.py: code used to identify and select the forecaster that performs best on the available training data 

Examples in the examples folder.
- forecaster_library_example
- forecaster_selector_example

Some notes about using the models:
- In dev/forecasters.ipynb the forecasters appear to perform poorly because...politics. 
- "srimax" forecaster is not that good and also may cause errors. In that case can add an if statement to skip it.
- As seen in example file, some forecasters require changing the hyperparameters prior to use, without that they will error out.

NEXT STEPS:
Train and test on the models on the GridWorks dataset
Goal: generate load forecasts based on previous load + weather data
X: weather, Y: load

## weather_forecast.zip

Code gathering weather forecast data from pvlib. 
- weather_forecast.ipynb stores the functions and provides an example. 
- weather_forecast.py contains the same code copy/pasted as a .py file so you can import the functions into other code. 

To use the weather forecasting tools you need an airport code, which i typically obtain from https://www.weather.gov/ using the following two steps
Some codes return errors from pvlib. I'm not entirely sure why. If you encounter errors you should be able to search for a nearby city (e.g. Oakland) and use the code for that location.
