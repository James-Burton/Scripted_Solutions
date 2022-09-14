# This script was a demo of the possibility included in R with regards to easily illustrating and sharing complex geospatial results.
# The primary purpose of this script was to enable First Nations to view Forest Harvest Overlaps over the available history of records.
# The data was compiled using a complex Python script, and this app was intended to reticulate the script and expand on the UI to enable such self contained functionality, or solely used to portray the results in a manageable way.
#
# All lines contained within this document were written in 2021 by James Burton.


setwd("[./secret/file/path/sorry]") # set your working directory
library(RColorBrewer)
library(shiny)
library(sf)
library(raster)
library(dplyr)
library(spData)
library(sp)
require(rgdal)
library(rgdal)
library(leaflet)
library(readxl)
library(leaflet.extras)
library(htmltools)
library(htmlwidgets) 


AOI <- rgdal::readOGR("[area/of/interest.geojson]") # This was a outer First Nation Boundary
AOI_Harv <- rgdal::readOGR("[primary/source/of/statistical/data.geojson]") # this was bcgw\FTEN_Harvest_Authority_SPW
AOI_TM_D_Housez <- rgdal::readOGR("[secondary/source/of/intersect/data.geojson]") # this was inner First Nation boundaries

exceldata=read_excel("[this/was/resultant/tabular/data/from/py_script.xlsx]")
dfdata=data.frame(exceldata)
dfdata

DaData <- merge(AOI_Harv, dfdata , 
                by.x = "TM", by.y = "Timber_Mark",
                duplicateGeoms = T)
DaData@data[1:5, ] ##check if merge
plot(DaData, main = "DaData")



palette_Value <- colorBin(c('#03071e',  
                            '#370617',
                            '#6a040f',
                            '#9d0208',
                            '#d00000',
                            '#dc2f02',
                            '#e85d04',
                            '#f48c06',
                            '#faa307',
                            '#ffba08'), 
                          bins = c(-80000,0,80000,160000,320000,480000,620000,730000,800000))
palette_Volume <- colorBin(c('#fee0d2',  
                             '#fcbba1',
                             '#fc9272',
                             '#fb6a4a',
                             '#ef3b2c',
                             '#cb181d',
                             '#a50f15',
                             '#67000d'), 
                           bins = c(-275,0,275,2600,7000,15000,50000,100000,201000))


## this is clutch to add a METRIC tool bar to right hand side of map.
## regular example is imperial and limited addMeasure() -> tres lame

mydrawPolylineOptions <- function (allowIntersection = TRUE, 
                                   drawError = list(color = "#b00b00", timeout = 2500), 
                                   guidelineDistance = 20, metric = TRUE, feet = FALSE, zIndexOffset = 2000, 
                                   shapeOptions = drawShapeOptions(fill = FALSE), repeatMode = FALSE) {
  leaflet::filterNULL(list(allowIntersection = allowIntersection, 
                           drawError = drawError, guidelineDistance = guidelineDistance, 
                           metric = metric, feet = feet, zIndexOffset = zIndexOffset,
                           shapeOptions = shapeOptions,  repeatMode = repeatMode)) }

spinPlugin <- htmlDependency(
  "spin.js", 
  "4.1.0",
  src = c(href = "https://cdnjs.cloudflare.com/ajax/libs/spin.js/2.3.2"),
  script = "spin.min.js") # there's no spin.css

leafletspinPlugin <- htmlDependency(
  "Leaflet.Spin", 
  "1.1.2",
  src = c(href = "https://cdnjs.cloudflare.com/ajax/libs/Leaflet.Spin/1.1.2"),
  script = "leaflet.spin.min.js")
registerPlugin <- function(map, plugin) {
  map$dependencies <- c(map$dependencies, list(plugin))
  map
}

# Note: Ctrl-Shift-J opens the javascript console in the browser
spin_event <- "function(el, x) {
  console.log('spin event added'); 
  var mymap = this;
  mymap.on('layerremove', function(e) {
    console.log('layerremove fired');
    mymap.spin(true);
  });
  mymap.on('layeradd', function(e) {
    console.log('layeradd fired');
    mymap.spin(false); 
  });
}"



ui <- bootstrapPage(
  tags$style(type = "text/css", "html, body {width:100%;height:100%}"),
  headerPanel(tags$h1("The First")),
  headerPanel(tags$h2("Automated First Nation")),
  headerPanel(tags$h3("Sumpage Report Maplette")),
  leafletOutput("map", 
                width = "100%", 
                height = "100%"
  ),
  absolutePanel(top = 10, right = 10,
                style="z-index:500;", # legend over my map (map z = 400)
                tags$h3(""), 
                sliderInput("periode", 
                            "Chronology",
                            min(DaData$Scaled_Year),
                            max(DaData$Scaled_Year),
                            value = range(DaData$Scaled_Year),
                            step = 1,
                            sep = ""
                )
  ),
  downloadButton("dl")
)



server <- function(input, output, session) {
  
  filteredData <- reactive({
    DaData[DaData$Scaled_Year >= input$periode[1] & DaData$Scaled_Year <= input$periode[2],]
  })
  
  output$map <- renderLeaflet({
    leaflet(DaData) %>%
      addProviderTiles("Esri.WorldImagery",
                       options = tileOptions(minZoom=6, maxZoom=16))%>%
      fitBounds(~min(-131.60412), ~min(56.46077), ~max(-129.3637), ~max(59.9987))%>%
      addDrawToolbar(
        polylineOptions = mydrawPolylineOptions(metric=TRUE, feet=FALSE),
        editOptions=editToolbarOptions(selectedPathOptions=selectedPathOptions())
      )%>%
      addPolygons(data=AOI)%>%
      addLayersControl(
        baseGroups = c("<span style='color: #7f0000; font-size: 11pt'><strong>Value</strong></span>", ## group 1
                       "Volume" ## group 2
        ),
        options = layersControlOptions(collapsed = FALSE))%>% ## we want our control to be seen right away
      
      addLegend(position = 'topleft', ## choose bottomleft, bottomright, topleft or topright
                colors = c('#fee0d2',
                           '#fcbba1',
                           '#fc9272',
                           '#fb6a4a',
                           '#ef3b2c',
                           '#cb181d',
                           '#a50f15',
                           '#67000d'), 
                labels = c('0%',"","","","","","",'26%'),  ## legend labels (only min and max)
                opacity = 0.6,      ##transparency again
                title = "Total<br>Volume",
                group="Volume") %>%  ## title of the legend
      addLegend(position = 'bottomright', ## choose bottomleft, bottomright, topleft or topright
                colors = c('#03071e',  
                           '#370617',
                           '#6a040f',
                           '#9d0208',
                           '#d00000',
                           '#dc2f02',
                           '#e85d04',
                           '#f48c06',
                           '#faa307',
                           '#ffba08'), 
                labels = c('-80,000$',"ringa","ringe","ringele","ringi","ringo","ringu","sometimes ringy","roger that dodger",'$800,000'),  ## legend labels (only min and max)
                opacity = 0.6,      ##transparency again
                title = "Total<br>Value",
                group="Value")   ## title of the legend
  })
  
  
  observe({
    leafletProxy("map") %>%
      
      registerPlugin(spinPlugin) %>% 
      registerPlugin(leafletspinPlugin) %>% 
      onRender(spin_event) %>% 
      clearShapes()%>%
      addPolygons(data = filteredData(),
                  label=~paste("Timber Mark: ",TM),
                  fillColor=~palette_Value(DaData$Cash_Value),  
                  fillOpacity = .25,         
                  color = "red",       ## color of borders between districts
                  weight = 1.5,            ## width of borders
                  #popup = popup1,         ## which popup?
                  group="Value",
                  highlightOptions = highlightOptions(color = "white",
                                                      weight = 2,
                                                      bringToFront = TRUE))%>%
      addPolygons(data = filteredData(),
                  label=~paste("Timber Mark: ",TM),
                  fillColor=~palette_Value(DaData$Total_Volume),  
                  fillOpacity = .25,         ## how transparent do you want the polygon to be?
                  color = "red",       ## color of borders between districts
                  weight = 1.5,            ## width of borders
                  #popup = popup1,         ## which popup?
                  group="Volume",
                  highlightOptions = highlightOptions(color = "white",
                                                      weight = 2,
                                                      bringToFront = TRUE))
  })
  output$dl <- downloadHandler(
    filename = "map.png",
    
    content = function(file) {
      mapshot(input[["map"]], file = file)
    })
  
}


shinyApp(ui, server)