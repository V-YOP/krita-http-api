// nodejs, benchmark

const PORT = 1976
const PARALLEL_NUM = 1
const REQUEST_BATCH_SIZE = 1000
const semaphare = mkSemaphare(8)

// code -> param
const ROUTES = {
    // 'ping': () => (''),  
    // 'thread-safe-test': () => '',
    // 'state/get': () => (''),
    // 'docker/list': () => (''),
    // 'docker/set-state':  () => ({
    //     "objectName": "MyToolbox",
    //     "visible": true,
    //     "floating": true
    // }),
    // 'view/list': () => '',
    // 'action/listen': () => '',
    "document/recorders": () => '',
    // "document/image": () => ({withImage: true}),
    // 'state/set': () => ({
    //     brushPreset: '粗糙硬边',
    //     foreground: [Math.random(), Math.random(),Math.random(),Math.random()],
    //     background: [Math.random(), Math.random(),Math.random(),Math.random()],
    //     brushSize: Math.random() * 100,
    //     brushRotation: Math.random() * 100,
    // }),
    // icon : () => ({"iconName": "select", "mode": "Normal", "state": "Off"}),
}

;((async () => {

    const tasks = Object.entries(ROUTES).map(([code, param]) => async () => {
        // 热身 
        for (let i = 0; i < 100; i++) {
            await request(code, param())
        }

        const times = []
        
        for (let i = 0; i < REQUEST_BATCH_SIZE; i++) {
            const tasks = []
            for (let j = 0; j < PARALLEL_NUM; j++) {
                tasks.push((async () => {
                    const a = +new Date()
                    await request(code, param())
                    const b = +new Date()
                    times.push(b - a)
                })())
            }
            await Promise.all(tasks)
        }
        const max = Math.max(...times)
        const min = Math.min(...times)
        const average = times.reduce((a, b) => a + b, 0) / times.length
        
        console.log(`code: ${code}, average: ${average} ms, max: ${max} ms, min: ${min} ms`)
    })

    for (const task of tasks) {
        await task()
    }

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
    await semaphare.wait()
    const res = await fetch(`http://localhost:${PORT}`, {body: JSON.stringify({code, param}), 'keepalive': true, method: 'POST'})
    const body = await res.json()
    if (!body.ok) {
        throw body
    }
    semaphare.signal()
    return body
}
