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

# Create user interface for app to make boxplot
ui <- (fluidPage(
  # Create title for app
  titlePanel("Time-Related Numerical Variables Against Shot Category After Implementaion"),
  # Sidebar layout for user input and output
  sidebarLayout(
    # Sidebar panel for user input
    sidebarPanel(
      # Create drop down menu for user to select categorical variable for x-axis (fixed as 'category')
      selectInput(inputId = "x", 
                  label = "X_Axis:", 
                  choices = c("category"), 
                  selected = "category" ),
      # Create drop down menu for user to select numerical variable for y-axis
      selectInput(inputId = "y",
                  label = "Y_Axis:",
                  choices = c("intaketime","dispatchtime","traveltime", "totalresponsetime", "time_on_scene", "totaltime"),
                  selected = "dispatchtime")
    ),
    # Main Panel to display output
    mainPanel = (
      # Output boxplot
      plotOutput(outputId = "boxplot")
    )
  )
)
)