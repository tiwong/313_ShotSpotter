# Load shiny library
library(shiny)

# Import Dataset
dataset3 <-read.csv("COMPLETE_SHOTSPOTTER_8_03_2023.csv", header= T)

# Create UI for app to make frequency histogram
ui <- fluidPage(
  
  # Create App Title
  titlePanel("ShotSpotter Histogram App"),
  
  # Sidebar layout for user input and output
  sidebarLayout(
    
    # Sidebar panel for user input
    sidebarPanel(
      
      # Create slider for user to input the number of bins
      sliderInput(inputId = "bins",
                  label = "Number of bins:",
                  min = 5,
                  max = 500,
                  value = 30)
      
    ),
    
    # Main Panel to display output
    mainPanel(
      
      # Outputs frequency histogram
      plotOutput(outputId = "distPlot")
      
    )
  )
)