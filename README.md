# 6.172 Project 4 &mdash; Leiserchess

## MCTS Search for board evaluation

---
## Player Repository
* Stores all versions of players.
* Allows for querying of download links for the players.

### Essential information
  * UUID for each player
  * Source code
  * Closest commit         (metadata)
  * User added comments    (metadata)

### Client
  * `upload_player.py <name> <comment>`
    * Uploads the current player directory, zipped, to the player repository service, which stores the player zip into AWS S3 and also stores the existence of said player.
    
### Server
  * `players.py`
    * Flask app that stores in an AWS RDS database
      1. player unique names
      2. UUIDs
      3. AWS S3 download link.

---

## Batch Autotest

---

## Game Viewer

---

## Other Notes
* Player `5a2be572-8401-4ee2-82a1-88859f4e89d5` - staff, original code


