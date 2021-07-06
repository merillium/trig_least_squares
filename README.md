##### This repo is currently a work in progress.

##### We use the [generalized solution](https://en.wikipedia.org/wiki/Trigonometric_interpolation#Solution_of_the_problem) to the trigonometric interpolation problem to create a trigonometric polynomial that interpolates (and extrapolates) from x- and y-values - which are provided by the user through the text boxes in the Dash Plotly framework. There is also error handling for invalid inputs.

##### Nice to have features: 
* ###### uploading two-column data
* ###### ability to specify how many of the points to interpolate
* ###### extrapolation of points not on the chart (e.g. evaluate f(10) for chart x range of [-5, 5])
* ###### specify the range of the function to display
* ###### display the interpolating trigonometric polynomial itself in summation & pi notation
  

##### Example below:
##### ![sample plot](https://github.com/merillium/trig_interpolation/blob/master/images/sample_dash_app.gif)
