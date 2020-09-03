use prueba_python;
# Verificando si se ha scrapeado todos los dias
select distinct(left(`Fecha Scrap.`,10)) from bbdd_productos;
# Creando la base maestro de productos
create view base_productos as 
select *, concat('P',lpad(row_number() over (order by Seccion,Nombre,Marca ),7,0)) as Llave from 
(select distinct Seccion,Nombre,Marca  from bbdd_productos) Base;
# Creando la base maestro de subcats
create view base_subcat as
select *, concat('S',lpad(row_number() over (order by Seccion ),4,0)) as Llave from 
(select distinct Categoria,Subcategoria,Seccion from bbdd_productos) Base;
# Creando la base normalizada
create view bbdd_normal as
select distinct `Fecha Scrap.`,c.Llave CodSeccion,b.Llave CodProd,`Precio Regular`,`Precio Actual`,`Precio Dscto.`,
`% Dscto.Reg.`,`% Dscto.Prom.` 
from bbdd_productos a
left join base_productos b 
on a.Seccion=b.Seccion and a.Nombre=b.Nombre and a.Marca=b.Marca
left join base_subcat c 
on a.Seccion=c.Seccion;



