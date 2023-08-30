# Load shiny library
library(shiny)

# Import Dataset
dataset3 <-read.csv("COMPLETE_SHOTSPOTTER_8_03_2023.csv", header= T)

# Create server to draw frequency histogram
server <- function(input, output) {

# Frequency histogram of complete ShotSpotter dataset with user input for bins
output$distPlot <- renderPlot({
  
  x <- dataset3$totalresponsetime
  x <- na.omit(x)
  
  bins <- seq(min(x), max(x), length.out = input$bins + 1)
  
  hist(x, breaks = bins, xlim=c(0,100), col = "black", border = "gold",
       xlab = " Total Response Time",
       main = "Frequency Histogram for Total Response Time to ShotSpotter Only Calls")
  
})

}