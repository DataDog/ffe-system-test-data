# Core IPC eligibility — November 27, 2026

Read-only source audit against FIT main e07ae57ef3108b18b10d2f67690bc36caf8303af. Eligibility is existing core transport/startup/harness wiring, not fresh build/runtime proof or implemented FeatureFlagService. All eligible rows must complete online precomputed before later modes.

| Platform | Source eligibility | Server/startup | Harness |
| --- | --- | --- | --- |
| Browser | Eligible | apps/web/src/ipc_executor.ts registers window.__ipc_execute__; scenario HTML loads executor | drivers/web.py → Playwright stubs |
| Android | Eligible | apps/android app IPCServer.kt; RumTestApplication starts core gRPC server | drivers/android.py → adb forwarded gRPC |
| iOS | Eligible | apps/ios RumTestApp/IPC/IpcServer.swift; RumTestAppApp starts server; Xcode Sources registration | drivers/ios.py → simulator gRPC |
| React Native | Eligible on both native hosts | Android IpcServer/IpcModule/IpcPackage; iOS IpcModule/IpcServer; App imports JS executor | drivers/react_native.py → native transport |
| Flutter | Eligible on native hosts | lib/ipc/ipc_server_io.dart; main.dart starts server using conditional import | drivers/flutter driver/platform delegation |
| KMP | Eligible on both native hosts | Android IPCServer/RumTestApplication; Apple IpcServer/RumTestAppApp and project registration | drivers/kotlin_multiplatform.py delegates to host |
| MAUI | Eligible | IPC/IpcServer.cs HttpListener/core dispatch; MauiProgram starts it | drivers/maui.py → HTTP/JSON, Android forwarding |
| Electron | Eligible through renderer executor | BrowserWindow loads existing Web scenarios/executor | drivers/electron.py → Playwright stubs; renderer proof does not establish main-process SDK capabilities |
| Unity | **Deferred: no established core** | No Unity app/driver tracked on inspected main | New unpublished candidate is not an established core/runtime foundation |

Unity preserved WIP at FIT base e613bea09f5b53e4a72c8ea435e137e25ee69bf4 adds IpcHost.cs and a UnityDriver. The host only accepts FeatureFlagService requests and returns 404 for other services. Documentation reports licence blocking before Editor compilation, with no player/runtime proof. Preserve it; establishing a new core is a separate prerequisite outside current row scope. Do not discard or count this candidate as accepted.

Shared dependency audit: RN's 19 changed native Android prerequisite files are a byte-identical subset of the Android 37-file candidate. WS-02 owns this common native SDK lane. WS-04 owns the native iOS prerequisite lane shared with RN. Old SDK conformance patches are salvage candidates rather than mandatory dependencies where recorded narrow exclusions suffice. Shared FIT overlays overlap extensively; WS-03 reconciles them once, excluding WS-01-owned files.
