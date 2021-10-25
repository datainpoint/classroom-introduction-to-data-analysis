#
# This is a Shiny web application. You can run the application by clicking
# the 'Run App' button above.
#
# Find out more about building applications with Shiny here:
#
#    http://shiny.rstudio.com/
#

library("shiny")
library("dplyr")
library("ggplot2")

time_series <- read.csv("time_series.csv")
time_series$Date <- as.Date(time_series$Date)
all_countries <- unique(time_series$Country_Region)
# Define UI for application
ui <- fluidPage(

    # Application title
    titlePanel("Covid19 Time Series Data"),

    # Sidebar with a slider input and a select input
    sidebarLayout(
        sidebarPanel(
            sliderInput("date", "Date Range:",
                        value = range(time_series$Date),
                        min = min(time_series$Date),
                        max = max(time_series$Date)),
            selectizeInput("country", "Country:",
                        choices = all_countries,
                        multiple = TRUE)
        ),

        # Show a plot of the generated line
        mainPanel(
           plotOutput("linePlot")
        )
    )
)

# Define server logic required to draw a line
server <- function(input, output) {

    output$linePlot <- renderPlot({
        filtered_time_series <- time_series %>%
            filter(Country_Region %in% input$country) %>% 
            filter(Date >= input$date[1]) %>% 
            filter(Date <= input$date[2])
        ggplot(filtered_time_series, aes(x = Date, y = Confirmed, colour = Country_Region)) +
            geom_line()
    })
}

# Run the application 
shinyApp(ui = ui, server = server)