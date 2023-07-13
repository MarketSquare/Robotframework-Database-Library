# Most important changes
- [added support for Teradata 15 & 16](https://github.com/MarketSquare/Robotframework-Database-Library/commit/ec8a62acad8ff63fce3edc07d6110851438bf9c7)
    ---> !TESTS ARE OK!!!
- [Solve encoding problem - explicitely use UTF8 when running SQL script files](https://github.com/MarketSquare/Robotframework-Database-Library/commit/3d0709168481e70caf18e61a3ca18f0680473e22)
    + https://github.com/MarketSquare/Robotframework-Database-Library/commit/01427be542142e71e85cf8929d988fa4971f980e
- [Support kingbase database](https://github.com/MarketSquare/Robotframework-Database-Library/commit/afddd4bf56def722c5b8e95b96424fd421df80e0)
    + https://github.com/MarketSquare/Robotframework-Database-Library/commit/287c3455bd863106fa0466d5e1ee9829d0fff627
    ---> THERE ARE NO TESTS AT ALL

- pyodbc - allow overriding dbDriver istead of always using "SQL Server"
    - https://github.com/MarketSquare/Robotframework-Database-Library/commit/27333ce101222846b0e3dc9ab65b9695245ec340
    - https://github.com/MarketSquare/Robotframework-Database-Library/commit/1a8295e2ac757b7d857dbd13e1e72fb7f05b1eb2
    - https://github.com/MarketSquare/Robotframework-Database-Library/commit/7d719d7b8c79515bacbe2cbff03919766faa5f7b
    - https://github.com/MarketSquare/Robotframework-Database-Library/commit/353253022da048259701dd14488245bab730e261

- PyODBC Tests:
    - https://github.com/MarketSquare/Robotframework-Database-Library/commit/1c7727eade8a1db3a2375463ab3a9752e8664990


- The keyword "Disconnect From Database" wouldn't fail if there was no open connection:
    - https://github.com/MarketSquare/Robotframework-Database-Library/commit/d3d0962c3c6eb9a6808371b559a9657bfe125796
    - My last commit

# Other minor improvements

# What I have done
- See issues
- Tests and CI
- Set charset when connecting via pyodbc