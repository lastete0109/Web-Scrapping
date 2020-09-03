drop database if exists `prueba_python`;
create database `prueba_python`;
use `prueba_python`;

set names utf8mb4;
set character_set_client = utf8mb4;

create table `bbdd_normal` (
`Fecha Scrap.` varchar(50),
`CodSeccion` varchar(10),
`CodProd` varchar(20),
`Precio Regular` float,
`Precio Actual` float,
`Precio Dscto.` float,
`% Dscto.Reg.` float,
`% Dscto.Prom.` float
) engine = InnoDB default charset = utf8mb4 collate = utf8mb4_0900_ai_ci;

create table `maestro_categorias` (
`CodSeccion` varchar(10),
`Categoria` varchar(50),
`Subcategoria` varchar(50),
`Seccion` varchar(50)
) engine = InnoDB default charset = utf8mb4 collate = utf8mb4_0900_ai_ci;

create table `maestro_productos` (
`CodProd` varchar(20),
`Seccion` varchar(50),
`Marca` varchar(50),
`Nombre` varchar(200)
) engine = InnoDB default charset = utf8mb4 collate = utf8mb4_0900_ai_ci;

