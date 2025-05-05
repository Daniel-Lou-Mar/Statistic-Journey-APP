# Trip Destination Recommender

A desktop application that helps you find the top 3 travel destinations from your departure city, based on your budget, travel dates, distance preferences and climate tastes. Under the hood it uses:

- The **Amadeus API** to discover nearby airports and flight offers  
- **OpenWeatherMap** to classify current climate in each destination  
- A **logistic regression** predictive model (trained on `viajes.csv`) to score each option by affinity  

---

## 🚀 Features

- **Customizable search parameters**  
  - Number of travelers  
  - Budget range (min & max price in EUR)  
  - Departure city  
  - Maximum flight distance (km)  
  - Departure & return dates (YYYY‑MM‑DD)  
  - Climate preference (`tropical`, `dry`, `polar`)  

- **Data sources & scoring**  
  1. **Nearby airports** within your maximum distance via Amadeus  
  2. **Best flight** for each airport (price, carrier, duration)  
  3. **Climate score** (1–10) by comparing actual temperature classification against your preference  
  4. **Predictive affinity** via a trained logistic‑regression model, using features:  
     - `per` (number of people)  
     - `dis` (distance in km)  
     - `din` (flight price in EUR)  
     - `nativo_extranjero` (same‑country flag)  
     - `preferencia_clima` (climate score)  

- **GUI**  
  Built with **Tkinter**: fill in the form, click **Realizar Consulta**, and see your top‑3 destinations with estimated price and probability.

---
