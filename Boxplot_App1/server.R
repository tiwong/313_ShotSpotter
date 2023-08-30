# Load libraries 'shiny' and 'ggplot2'
library(shiny)
library(ggplot2)

# Import dataset
dataset2 <- read.csv("All_Shots_After_Implementation_8_13_23.csv", header= T)

# Omit NA Values for time-related numerical variables
dataset2 <- dataset2[!(is.na(dataset2$intaketime)),]
dataset2<- dataset2[! (is.na(dataset2$dispatchtime)),]
dataset2<- dataset2[! (is.na(dataset2$traveltime)),]
dataset2 <- dataset2[! (is.na(dataset2$totalresponsetime)),] 
dataset2 <- dataset2[!(is.na(dataset2$time_on_scene)),]
dataset2<- dataset2[!(is.na(dataset2$totaltime)),]
dataset2<- dataset2[!(is.na(dataset2$category)),]

# Factor category since it is a categorical variable
dataset2$category = as.factor(dataset2$category)

# Create server to draw boxplot
server <- (function(input, output, session) {
  output$boxplot <- renderPlot({
    
    # Boxplot of time-related numerical variables vs. shot category
    ggplot(data=dataset2, aes_string(x = input$x, y = input$y)) + 
      geom_boxplot() +
      geom_boxplot(outlier.colour=NA) +
      scale_y_continuous(limits=c(0,70), breaks=seq(0,100,5), expand = c(0, 0))
  }
  )
}
)