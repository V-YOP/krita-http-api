// nodejs, benchmark
const { performance } = require('perf_hooks');
const PORT = 1976
const PARALLEL_NUM = 3
const REQUEST_BATCH_SIZE = 3000
const semaphare = mkSemaphare(8)

// code -> param
const ROUTES = {
    'ping': () => (''),  
    'thread-safe-test': () => '',
    'state/get': () => (''),
    'docker/list': () => (''),
    // 'docker/set-state':  () => ({
    //     "objectName": "MyToolbox",
    //     "visible": true,
    //     "floating": true
    // }),
    'view/list': () => '',
    'action/listen': () => '',
    "document/records": () => '',
    // "document/image": () => ({withImage: true}),
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
                    const a = performance.now()
                    await request(code, param())
                    const b = performance.now()
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

/*
homemade: 

1 thread x 3000

code: ping, average: 2.3396829324563346 ms, max: 5.84309995174408 ms, min: 1.5795000791549683 ms
code: thread-safe-test, average: 2.354180166363716 ms, max: 10.479699969291687 ms, min: 1.5587999820709229 ms
code: state/get, average: 2.5064013003905616 ms, max: 6.882399916648865 ms, min: 1.7879000902175903 ms
code: docker/list, average: 3.1399855347474417 ms, max: 6.983299970626831 ms, min: 2.3391000032424927 ms
code: view/list, average: 2.3911871652205785 ms, max: 9.501699924468994 ms, min: 1.624899983406067 ms
code: action/listen, average: 2.2905263665914535 ms, max: 7.616699934005737 ms, min: 1.5374000072479248 ms
code: document/records, average: 2.921222499847412 ms, max: 11.214599967002869 ms, min: 2.0827999114990234 ms
code: icon, average: 3.7696206990480423 ms, max: 9.865400075912476 ms, min: 2.825800061225891 ms

3 threads x 3000

code: ping, average: 4.403632567246755 ms, max: 17.958099961280823 ms, min: 2.0611000061035156 ms
code: thread-safe-test, average: 4.684364255865415 ms, max: 21.565600037574768 ms, min: 2.1104999780654907 ms
code: state/get, average: 5.199909133844906 ms, max: 23.154900074005127 ms, min: 2.2348999977111816 ms
code: docker/list, average: 6.556706377453274 ms, max: 31.828099966049194 ms, min: 2.8524999618530273 ms
code: view/list, average: 4.579258978115187 ms, max: 15.919399976730347 ms, min: 2.1749000549316406 ms
code: action/listen, average: 4.681412778072887 ms, max: 23.169899940490723 ms, min: 2.078499913215637 ms
code: document/records, average: 5.870700845228301 ms, max: 22.369499921798706 ms, min: 2.673900008201599 ms
code: icon, average: 7.815499977866809 ms, max: 30.889600038528442 ms, min: 3.4364999532699585 ms

FastAPI: 


*/