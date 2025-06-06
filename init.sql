-- Script d'initialisation de la base de données

-- Création de la base de données (si elle n'existe pas déjà)
-- PostgreSQL crée automatiquement la base définie dans POSTGRES_DB
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    age SERIAL ,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price NUMERIC(10, 2) NOT NULL,
    category VARCHAR(255) ,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Insertion de données d'exemple pour les utilisateurs
INSERT INTO users (name, email, age, created_at) VALUES
('Alice Martin', 'alice@example.com', 28, NOW()),
('Bob Dupont', 'bob@example.com', 35, NOW()),
('Claire Dubois', 'claire@example.com', 42, NOW()),
('David Lambert', 'david@example.com', 31, NOW()),
('Emma Rousseau', 'emma@example.com', 27, NOW())
ON CONFLICT (email) DO NOTHING;

-- Insertion de données d'exemple pour les produits
INSERT INTO products (name, description, price, category, created_at) VALUES
('Smartphone Samsung Galaxy', 'Smartphone Android dernière génération avec écran AMOLED', 799.99, 'Électronique', NOW()),
('MacBook Pro 14"', 'Ordinateur portable Apple avec puce M2', 2199.99, 'Électronique', NOW()),
('T-shirt Adidas', 'T-shirt de sport en coton respirant', 29.99, 'Vêtements', NOW()),
('Jean Levi''s 501', 'Jean classique coupe droite', 89.99, 'Vêtements', NOW()),
('Café Bio Éthiopien', 'Café en grains torréfaction artisanale', 15.99, 'Alimentation', NOW()),
('Chocolat Noir 70%', 'Tablette de chocolat noir premium', 4.99, 'Alimentation', NOW()),
('Le Petit Prince', 'Roman classique d''Antoine de Saint-Exupéry', 12.99, 'Livres', NOW()),
('1984 - George Orwell', 'Roman dystopique incontournable', 14.99, 'Livres', NOW()),
('Ballon de Football Nike', 'Ballon officiel FIFA', 39.99, 'Sport', NOW()),
('Raquette de Tennis Wilson', 'Raquette professionnelle', 149.99, 'Sport', NOW());

-- Création d'index pour optimiser les performances
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_price ON products(price);
CREATE INDEX IF NOT EXISTS idx_products_created_at ON products(created_at);



