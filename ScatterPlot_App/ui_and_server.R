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

# Create UI for app to make scatterplot
ui <- (fluidPage(
  # Create title for app
  titlePanel("ShotSpotter Only Calls Numerical Variable Comparison Scatterplots"),
  # Sidebar layout for user input and output
  sidebarLayout(
    # Sidebar panel for user input
    sidebarPanel(
      # Create drop down menu for user to select numerical variable for x-axis 
      selectInput(inputId = "x", 
                  label = "X_Axis:", 
                  choices = c("intaketime","dispatchtime","traveltime", "totalresponsetime", "time_on_scene", "totaltime"), 
                  selected = "intaketime" ),
      # Create drop down menu for user to select numerical variable for y-axis
      selectInput(inputId = "y",
                  label = "Y_Axis:",
                  choices = c("intaketime","dispatchtime","traveltime", "totalresponsetime", "time_on_scene", "totaltime"),
                  selected = "dispatchtime")
    ),
    # Main Panel to display output
    mainPanel = (
      # Outputs scatterplot
      plotOutput(outputId = "scatterplot")
    )
  )
)
)

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

shinyApp(ui, server)
