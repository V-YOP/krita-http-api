// nodejs, benchmark
// const { performance } = require('perf_hooks');
// const PORT = 1976
// const PARALLEL_NUM = 3
// const REQUEST_BATCH_SIZE = 3000
// const semaphare = mkSemaphare(8)

// // code -> param
// const ROUTES = {
//     'ping': () => (''),  
//     'thread-safe-test': () => '',
//     'state/get': () => (''),
//     'docker/list': () => (''),
//     // 'docker/set-state':  () => ({
//     //     "objectName": "MyToolbox",
//     //     "visible": true,
//     //     "floating": true
//     // }),
//     'view/list': () => '',
//     'action/listen': () => '',
//     "document/records": () => '',
//     // "document/image": () => ({withImage: true}),
//     // 'state/set': () => ({
//     //     brushPreset: '粗糙硬边',
//     //     foreground: [Math.random(), Math.random(),Math.random(),Math.random()],
//     //     background: [Math.random(), Math.random(),Math.random(),Math.random()],
//     //     brushSize: Math.random() * 100,
//     //     brushRotation: Math.random() * 100,
//     // }),
//     icon : () => ({"iconName": "select", "mode": "Normal", "state": "Off"}),
// }

// ;((async () => {

//     const tasks = Object.entries(ROUTES).map(([code, param]) => async () => {
//         // 热身 
//         for (let i = 0; i < 100; i++) {
//             await request(code, param())
//         }

//         const times = []
        
//         for (let i = 0; i < REQUEST_BATCH_SIZE; i++) {
//             const tasks = []
//             for (let j = 0; j < PARALLEL_NUM; j++) {
//                 tasks.push((async () => {
//                     const a = performance.now()
//                     await request(code, param())
//                     const b = performance.now()
//                     times.push(b - a)
//                 })())
//             }
//             await Promise.all(tasks)
//         }
//         const max = Math.max(...times)
//         const min = Math.min(...times)
//         const average = times.reduce((a, b) => a + b, 0) / times.length
        
//         console.log(`code: ${code}, average: ${average} ms, max: ${max} ms, min: ${min} ms`)
//     })

//     for (const task of tasks) {
//         await task()
//     }

// })().catch(console.error));



// function mkSemaphare(count = 5) {
//     const cbs = []
//     return {
//         wait: () => new Promise(resolve => {
//             if (count > 0) {
//                 resolve()
//                 count--
//             } else {
//                 cbs.push(() => resolve())
//             }
//         }),
//         signal: () => {
//             count++
//             const cb = cbs.shift()
//             cb && cb()
//         }
//     }
// }

// async function request(code, param) {
//     await semaphare.wait()
//     const res = await fetch(`http://localhost:${PORT}`, {body: JSON.stringify({code, param}), 'keepalive': true, method: 'POST'})
//     const body = await res.json()
//     if (!body.ok) {
//         throw body
//     }
//     semaphare.signal()
//     return body
// }


const { performance } = require('perf_hooks');
const PORT = 1976
const PARALLEL_NUM = 1
const REQUEST_BATCH_SIZE = 3000

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

const WebSocket = require('ws');

// 创建 WebSocket 客户端实例
const ws = new WebSocket('ws://localhost:1949');  // 替换为你的 WebSocket 服务器地址


const waitOpen = new Promise(resolve => {
    // 连接成功时的回调
    ws.on('open', function open() {
        console.log('Connected to WebSocket server');
        resolve()
        // 向服务器发送消息
    });
})

function waitMessage() {
    return new Promise(resolve => {
        function go(data) {
            resolve(JSON.parse(data.toString('utf-8')))
        }
        ws.once('message', go)
    })
}

// 处理错误
ws.on('error', function error(err) {
  console.error('WebSocket error:', err);
});

// 处理连接关闭
ws.on('close', function close() {
  console.log('Disconnected from WebSocket server');
});


async function request(code, param) {
    ws.send(JSON.stringify({code, param}))
    const res = await waitMessage()
    if (!res.ok) {
        throw res
    }
    return res
}




;((async () => {
    await waitOpen
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
/*

HTTP: 
1 thread x 3000
code: ping, average: 2.3396829324563346 ms, max: 5.84309995174408 ms, min: 1.5795000791549683 ms
code: thread-safe-test, average: 2.354180166363716 ms, max: 10.479699969291687 ms, min: 1.5587999820709229 ms
code: state/get, average: 2.5064013003905616 ms, max: 6.882399916648865 ms, min: 1.7879000902175903 ms
code: docker/list, average: 3.1399855347474417 ms, max: 6.983299970626831 ms, min: 2.3391000032424927 ms
code: view/list, average: 2.3911871652205785 ms, max: 9.501699924468994 ms, min: 1.624899983406067 ms
code: action/listen, average: 2.2905263665914535 ms, max: 7.616699934005737 ms, min: 1.5374000072479248 ms
code: document/records, average: 2.921222499847412 ms, max: 11.214599967002869 ms, min: 2.0827999114990234 ms
code: icon, average: 3.7696206990480423 ms, max: 9.865400075912476 ms, min: 2.825800061225891 ms

Websocket: 
1 thread x 3000
code: ping, average: 1.9788807993332544 ms, max: 29.830899953842163 ms, min: 1.3082998991012573 ms
code: thread-safe-test, average: 1.8286754351854324 ms, max: 5.117599964141846 ms, min: 1.3509999513626099 ms
code: state/get, average: 2.0560419683853786 ms, max: 8.570000052452087 ms, min: 1.523900032043457 ms
code: docker/list, average: 2.7198636332352955 ms, max: 6.729900002479553 ms, min: 2.0305999517440796 ms
code: view/list, average: 1.9603952338298163 ms, max: 14.642099976539612 ms, min: 1.4101999998092651 ms
code: action/listen, average: 1.848827399969101 ms, max: 19.598099946975708 ms, min: 1.31440007686615 ms
code: document/records, average: 2.5956327004035313 ms, max: 7.910499930381775 ms, min: 1.9453999996185303 ms
code: icon, average: 3.3410960670312244 ms, max: 15.367900013923645 ms, min: 2.5363000631332397 ms

*/