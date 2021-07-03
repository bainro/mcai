/**
 * Script to login as mineflayer bot, follow around a player,
 * and save reward signal to csv. Need to specify recording
 * location and duration when invoking on the cmd line.
 */

const mineflayer = require('mineflayer')
const { pathfinder, Movements, goals: { GoalNear } } = require('mineflayer-pathfinder')
const mineflayerViewer = require('prismarine-viewer').mineflayer
const Entity = require('prismarine-entity')
const createCsvWriter = require('csv-writer').createObjectCsvWriter;
var fs = require('fs');

const RANGE_GOAL = 5 // get within this radius of the player

if (process.argv.length != 4) {
  console.log('Usage : node rewards.js <save_location> <record_duration>')
  process.exit(1)
}

results_dir  = process.argv[2];
run_duration = process.argv[3];

if (results_dir.slice(-1) != "\\") {
    results_dir += "\\"
}

if (!fs.existsSync(results_dir)){
    fs.mkdirSync(results_dir);
}

const csvWriter = createCsvWriter({
  path: results_dir + 'rewards.csv',
  header: [
    {id: 'reward', title: 'Reward'},
    {id: 'time', title: 'Time'}
  ]
});

let datalog = [];

host     = process.env.MC_HOST
port     = process.env.MC_PORT
username = process.env.MC_USERNAME
passwd   = process.env.MC_PASSWD
follow   = process.env.MC_FOLLOW // username of who to track

missing_creds = (typeof(host) == "undefined" || typeof(port) == "undefined")
missing_creds = (missing_creds || typeof(username) == "undefined")
missing_creds = (missing_creds || typeof(passwd) == "undefined")
missing_creds = (missing_creds || typeof(follow) == "undefined")

if (missing_creds) {
    console.log("missing bot login credentials in BASH env")
    console.log("powershell syntax: $env:MC_HOST='localhost'")
    process.exit(69);
}

const bot = mineflayer.createBot({
    host: host,
    port: port,
    username: username,
    password: passwd
})

bot.loadPlugin(pathfinder)

bot.once('spawn', () => {
    mineflayerViewer(bot, { port: 6006, firstPerson: false })
    bot.chat("going to make myself invisible via spectator mode!")
    bot.chat("/gamemode spectator")
})

// convert Date() to unix timestamp units of seconds
var lastRun = new Date().getTime() / 1000
var startTime = new Date().getTime() / 1000
var lastHealth = null
var alive = false

bot.on('physicsTick', () => {
    currTime = new Date().getTime() / 1000
    // update about 20x per second
    if (lastRun + 0.05 > currTime) return

    const mcData = require('minecraft-data')(bot.version)
    const defaultMove = new Movements(bot, mcData)

    // this question mark syntax is confusing...
    const target = bot.players[follow]?.entity
    
    if (!target) {
        console.log("I don't see you! :(")
        if (alive) {
            // ensure only penalize once per death and
            // only after the bot has finished setting up
            console.log("-20 for dying!")
            datalog.push({
                reward: -20,
                time: new Date().getTime() / 1000
            })
        }
        alive = false
        return
    }

    alive = true

    if (lastHealth == null) {
        lastHealth = target.metadata[8]
    }

    currHealth = target.metadata[8]
    healthDelta = currHealth - lastHealth
    if (healthDelta != 0 && healthDelta != 20) {
        console.log("health reward: ", healthDelta)
        datalog.push({
            reward: healthDelta,
            time: new Date().getTime() / 1000
        })
        lastHealth = currHealth
    }

    // another odd syntax, but I'll allow it
    const { x: playerX, y: playerY, z: playerZ } = target.position

    bot.pathfinder.setMovements(defaultMove)
    bot.pathfinder.setGoal(new GoalNear(playerX, playerY, playerZ, RANGE_GOAL))

    lastRun = new Date().getTime() / 1000

    if (lastRun - startTime > run_duration) {
        csvWriter
            .writeRecords(datalog)
            .then(() => {
                console.log('The csv file was written successfully')
                process.exit(0)
            });
    }
})

bot._client.on('spawn_entity_experience_orb', (packet) => {
    console.log("+1 for spawning exp orbs!")
    datalog.push({
        reward: 1,
        time: new Date().getTime() / 1000
    })
})

bot.on("death", () => {
    bot.chat("i died somehow")
})