-- =====================================================
-- ESQUEMA DE BASE DE DATOS PARA API_EVALUAR_FEPA
-- =====================================================

-- Tabla principal: evaluacion_fepa
-- Almacena cada evaluación realizada con el porcentaje y fecha
CREATE TABLE IF NOT EXISTS evaluacion_fepa (
    ideval INT PRIMARY KEY AUTO_INCREMENT,
    fechahora DATETIME NOT NULL,
    porcentaje DECIMAL(3,2) NOT NULL
);

-- Tabla de detalle: evaldet_fepa
-- Almacena los emails de los comentadores con mayor promedio de palabras
CREATE TABLE IF NOT EXISTS evaldet_fepa (
    id INT PRIMARY KEY AUTO_INCREMENT,
    ideval INT NOT NULL,
    userId INT NOT NULL,
    email VARCHAR(255) NOT NULL,
    promedio DECIMAL(5,2) NOT NULL,
    FOREIGN KEY (ideval) REFERENCES evaluacion_fepa(ideval) ON DELETE CASCADE
);
