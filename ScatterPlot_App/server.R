# Load libraries 'shiny' and 'ggplot2'
library(shiny)
library(ggplot2)

# Import dataset
dataset1 <-read.csv("ShotSpotter_Complete_8_17_23.csv", header= T)

# Omit na values from dataset for time-related numerical variables
dataset1 <- dataset1[!(is.na(dataset1$intaketime)),]
dataset1<- dataset1[! (is.na(dataset1$traveltime)),]
dataset1<- dataset1[! (is.na(dataset1$dispatchtime)),]
dataset1 <- dataset1[! (is.na(dataset1$totalresponsetime)),] 
dataset1 <- dataset1[!(is.na(dataset1$time_on_scene)),]
dataset1<- dataset1[!(is.na(dataset1$totaltime)),]

# Create server to draw scatterplot
server <- (function(input, output, session) {
  output$scatterplot <- renderPlot({
    
    # Scatterplot of time-related numerical variables for complete ShotSpotter dataset 
    ggplot(data=dataset1, aes_string(x = input$x, y = input$y)) + 
      geom_point()
  }
  )
}
)
