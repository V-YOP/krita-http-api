// nodejs, benchmark

const PORT = 8000
const PARALLEL_NUM = 5
const REQUEST_BATCH_SIZE = 100
const semaphare = mkSemaphare(100)

// code -> param
const ROUTES = {
    'ping': () => ({}),  
    'state/get': () => ({}),
    'docker/list': () => ({}),
    // 'docker/set-state':  () => ({
    //     "objectName": "MyToolbox",
    //     "visible": true,
    //     "floating": true
    // }),
    // 'state/set': () => ({
    //     brushPreset: '粗糙硬边',
    //     foreground: [Math.random(), Math.random(),Math.random(),Math.random()],
    //     background: [Math.random(), Math.random(),Math.random(),Math.random()],
    //     brushSize: Math.random() * 100,
    //     brushRotation: Math.random() * 100,
    // }),
    icon : () => ({"iconName": "select", "mode": "Normal", "state": "Off"}),
}

;((async () => {
    for (let i = 0; i < REQUEST_BATCH_SIZE; i++) {
        await Promise.all([
            fetch('http://localhost:' + PORT),
            fetch('http://localhost:' + PORT),
            fetch('http://localhost:' + PORT),
            fetch('http://localhost:' + PORT),
            fetch('http://localhost:' + PORT),
            fetch('http://localhost:' + PORT),
            fetch('http://localhost:' + PORT),
            fetch('http://localhost:' + PORT),
            fetch('http://localhost:' + PORT),
            fetch('http://localhost:' + PORT),
            fetch('http://localhost:' + PORT),
            fetch('http://localhost:' + PORT),
            fetch('http://localhost:' + PORT),
            fetch('http://localhost:' + PORT),
            fetch('http://localhost:' + PORT),])
    }


    // const tasks = Object.entries(ROUTES).map(([code, param]) => async () => {
    //     // 热身 
    //     for (let i = 0; i < 20; i++) {
    //         await request(code, param())
    //     }

    //     const times = []

    //     for (let i = 0; i < REQUEST_BATCH_SIZE; i++) {
    //         const tasks = []
    //         for (let j = 0; j < PARALL   EL_NUM; j++) {
    //             tasks.push((async () => {
    //                 const a = +new Date()
    //                 await request(code, param())
    //                 const b = +new Date()
    //                 times.push(b - a)
    //             })().catch(console.error))
    //         }
    //         await Promise.all(tasks)
    //     }
    //     const max = Math.max(...times)
    //     const min = Math.min(...times)
    //     const average = times.reduce((a, b) => a + b, 0) / times.length
        
    //     console.log(`code: ${code}, average: ${average} ms, max: ${max} ms, min: ${min} ms`)
        
    // })

    // for (const task of tasks) {
    //     await task()
    // }

})().catch(console.error));



function mkSemaphare(count = 5) {
    const cbs = []
    return {
        wait: () => new Promise(resolve => {
            if (count > 0) {
                resolve()
                count--
            } else {
                cbs.push(() => resolve())
            }
        }),
        signal: () => {
            count++
            const cb = cbs.shift()
            cb && cb()
        }
    }
}

async function request(code, param) {
    const res = await fetch(`http://localhost:${PORT}`, {method: 'GET'})
    return res
}
