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

# Create server to draw frequency histogram
server <- function(input, output) {
  
  # Frequency histogram of complete ShotSpotter dataset with user input for bins
  output$distPlot <- renderPlot({
    
    # Let X represent totalresponsetime
    x <- dataset3$totalresponsetime
    # Omit observations with NA values for totalresponsetime
    x <- na.omit(x)
    
    # Allows our histogram to plot however many bins the user chooses within the domain of the minimum and maximum 
    bins <- seq(min(x), max(x), length.out = input$bins + 1)
    
    # Plot frequency histogram
    # Use (0,100) as the domain for the x-axis
    # Choose colors to fill and outline histogram
    hist(x, breaks = bins, xlim=c(0,100), col = "black", border = "gold",
         # Label x-axis
         xlab = " Total Response Time",
         # Title for Frequency Histogram
         main = "Frequency Histogram for Total Response Time to ShotSpotter Only Calls")
    
  })
  
}

shinyApp(ui, server)
