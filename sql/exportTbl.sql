use database_name
go

create table dbo.exportTbl
(
    ID             int not null,
    ModelNumer     nvarchar(16),
    Longitude      nvarchar(16),
    Latitude       nvarchar(16),
    ModelOwner     nvarchar(3),
    ModelType      nvarchar,
    Address        nvarchar(128),
    Height         float,
    ModelYear      nvarchar(4),
    City           nvarchar(64),
    Description    nvarchar(1600),
    Status         nvarchar,
    ProgressStatus nvarchar,
    ProcessDate    date
)
go
