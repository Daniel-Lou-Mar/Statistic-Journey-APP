library(here)

viajes <- read.csv(here("viajes.csv"))
modelo.logit <- glm(admit ~ per + mood + dis + din + nativo_extranjero + preferencia_clima, data = viajes, family = binomial(link = "logit"))

library(shiny)
library(shinythemes)
library(bslib)

mi_tema <- bs_theme(
  version = 5,
  bootswatch = "minty",
  primary = "blue",   # Color primario
  secondary = "blue", # Color secundario
  base_font = font_google("Roboto"),  # Fuente base
  heading_font = font_google("Roboto")  # Fuente para encabezados
)



ui <- fluidPage(
  tags$head(tags$title("Predicción de Viaje")),
  
  # Logo
  tags$img(src = "logo.png", height = "150px", style = "display: block; margin-left: auto; margin-right: auto;"),
  
  theme = mi_tema,
  div(
    h1("SkyScanner Modelo Logit Predictivo ¿Irá de viaje? ", 
       style = "text-align: center; font-weight: bold; color: black;")
  ),
  br(),
  sidebarLayout(
    sidebarPanel(
      h4("Introduce los datos del viaje:"),
      sliderInput("per", "👫 Número de acompañantes:", min = 0, max = 10, value = 3),
      sliderInput("mood", "Nivel de tranquilidad del destino:", min = 0, max = 10, value = 6),
      sliderInput("dis", "⇔ Distancia al destino (km):", min = 0, max = 5000, value = 1000, step = 100),
      sliderInput("din", "€ Coste estimado:", min = 0, max = 5000, value = 600, step = 50),
      selectInput("nativo_extranjero", "🗣 Idioma en destino:",
                  choices = c("Nativo" = 0, "Extranjero" = 1)),
      sliderInput("preferencia_clima", "🌦 Previsión climática (0-10):", min = 0, max = 10, value = 7),
      br(),
      actionButton("predecir", "Predecir si viaja", class = "btn btn-success btn-lg")
    ),
    mainPanel(
      br(),
      h3("Resultado de la predicción:"),
      br(),
      wellPanel(
        style = "background-color: #A1EBD1; border-left: 5px solid: #A1EBD1",
        uiOutput("resultado")
      )
    )
  )
)



# Servidor dataframe/modelo
server <- function(input, output) {
  
  observeEvent(input$predecir, {
    
    # Creamos un nuevo dataframe con los valores que mete el usuario
    x.new <- data.frame(
      per = input$per,
      mood = input$mood,
      dis = input$dis,
      din = input$din,
      nativo_extranjero = as.numeric(input$nativo_extranjero),
      preferencia_clima = input$preferencia_clima
    )
    
    # Calculamos la probabilidad usando el entrenado
    prob <- predict(modelo.logit, x.new, type = "response")
    
    # Texto que se va a mostrar
    mensaje <- sprintf("La probabilidad de que el usuario viaje es de %.1f%%.\n", prob * 100)
    
    # Daterminar si viaja o no
    if (prob >= 0.5) {
      mensaje <- paste0(mensaje, "Diremos que SÍ irá de viaje.")
    } else {
      mensaje <- paste0(mensaje, "Diremos que NO irá de viaje.")
    }
    
    # Mostramos el resultado por pantalla
    output$resultado <- renderUI({ 
      tags$div(style = "color: white; font-size: 18px; line-height: 1.6;",
               mensaje)
    })
  })
}

# Ejecutar la app
shinyApp(ui = ui, server = server)





