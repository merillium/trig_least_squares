##### This repo is currently a work in progress.

##### We solve the least squares problem using trigonometric polynomials up to degree 10. There is also error handling for invalid inputs.

##### Current features:
- [x] uploading csvs with the option to select columns corresponding to x- and y- variables
- [x] error handling for invalid csvs or data
- [x] display the interpolating trigonometric polynomial within the chart

##### Features in progress: 
- [ ] ability to select the index of the dataframe (convenient for timeseries data)
- [ ] extrapolation of points not on the chart (e.g. evaluate f(10) for chart x range of [-5, 5])
- [ ] specify the range of the function to display
- [ ] calculate and show metrics determining the least squares fit (r<sup>2</sup>)
- [ ] ability to modify the period of the basis functions (this might be important for more practical applications such as real data sets)

##### Example below:
##### ![sample plot]()
