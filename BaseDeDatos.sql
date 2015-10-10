USE MASTER
GO
CREATE DATABASE Dw_NorthWindFinanzas
on PRIMARY
(
	name='Dw_FinanzasData',
	filename='D:\DATA\Dw_FinanzasData.MDF',
	size=5mb,
	maxsize = unlimited,
	filegrowth=10%
)
log on (
	name='Dw_FinanzasLog',
	filename='D:\DATA\Dw_FinanzasData.LDF',
	size = 1mb,
	maxsize = unlimited,
	filegrowth= 10%
)
go
----------------------------------------------------
CREATE TABLE Dim_Clientes
(
	[CustomerKey] [nchar](5) primary key NOT NULL,
	[CompanyName] [nvarchar](40) NOT NULL,
	[City] [nvarchar](15) NULL,
	[Region] [nvarchar](15) NULL,
	[Country] [nvarchar](15) NULL,
)
CREATE TABLE Dim_Ordenes
(
	[OrderKey] [int] IDENTITY(10248,1) primary key NOT NULL,
	[OrderDate] [datetime] NULL,
	
)

CREATE TABLE Dim_Empleados
(
	[EmployeeKey] [int] IDENTITY(1,1) primary key NOT NULL,
	[EmployeeName] [nvarchar](50) NOT NULL,
	[HireDate] [datetime] NULL,
	
)

CREATE TABLE Dim_Locales
(
	[TerritoryKey] [nvarchar](20) NOT NULL,
	[TerritoryDescription] [nchar](50) NOT NULL,
	[RegionDescription] [int] NOT NULL,
)

CREATE TABLE Dim_Proveedores
(
	[SupplierKey] [int] IDENTITY(1,1) primary key NOT NULL,
	[CompanyName] [nvarchar](40) NOT NULL,
	[City] [nvarchar](15) NULL,
	[Region] [nvarchar](15) NULL,
	[Country] [nvarchar](15) NULL,
)

CREATE TABLE Fact_Ventas
(
	VentasKey int identity (1,1) ,
	[CustomerKey] [nchar](5),
	[EmployeeKey] [int] ,
	[TerritoryKey] [nvarchar](20),
	[SupplierKey] [int],
	[Fechakey] datetime,
	[PrecioTotal] money,
	CantidadTotal decimal(8,2),
	GeneralTotal money
)
