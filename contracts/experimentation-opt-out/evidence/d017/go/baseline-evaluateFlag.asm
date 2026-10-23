
/tmp/d017-go-evidence/baseline.test:     file format elf64-x86-64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

0000000000e6a200 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag>:
  e6a200:	4c 8d a4 24 78 ff ff 	lea    -0x88(%rsp),%r12
  e6a207:	ff
  e6a208:	4d 3b 66 10          	cmp    0x10(%r14),%r12
  e6a20c:	0f 86 5e 08 00 00    	jbe    e6aa70 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x870>
  e6a212:	55                   	push   %rbp
  e6a213:	48 89 e5             	mov    %rsp,%rbp
  e6a216:	48 81 ec 00 01 00 00 	sub    $0x100,%rsp
  e6a21d:	48 89 9c 24 38 01 00 	mov    %rbx,0x138(%rsp)
  e6a224:	00
  e6a225:	48 89 8c 24 40 01 00 	mov    %rcx,0x140(%rsp)
  e6a22c:	00
  e6a22d:	4c 89 8c 24 60 01 00 	mov    %r9,0x160(%rsp)
  e6a234:	00
  e6a235:	48 8d 54 24 50       	lea    0x50(%rsp),%rdx
  e6a23a:	44 0f 11 3a          	movups %xmm15,(%rdx)
  e6a23e:	44 0f 11 7a 10       	movups %xmm15,0x10(%rdx)
  e6a243:	44 0f 11 7a 20       	movups %xmm15,0x20(%rdx)
  e6a248:	44 0f 11 7a 30       	movups %xmm15,0x30(%rdx)
  e6a24d:	44 0f 11 7a 38       	movups %xmm15,0x38(%rdx)
  e6a252:	48 85 c0             	test   %rax,%rax
  e6a255:	0f 84 af 00 00 00    	je     e6a30a <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x10a>
  e6a25b:	80 78 10 00          	cmpb   $0x0,0x10(%rax)
  e6a25f:	90                   	nop
  e6a260:	74 4f                	je     e6a2b1 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0xb1>
  e6a262:	48 89 84 24 30 01 00 	mov    %rax,0x130(%rsp)
  e6a269:	00
  e6a26a:	48 89 bc 24 48 01 00 	mov    %rdi,0x148(%rsp)
  e6a271:	00
  e6a272:	4c 89 44 24 40       	mov    %r8,0x40(%rsp)
  e6a277:	48 89 74 24 38       	mov    %rsi,0x38(%rsp)
  e6a27c:	4c 89 8c 24 b8 00 00 	mov    %r9,0xb8(%rsp)
  e6a283:	00
  e6a284:	48 89 8c 24 40 01 00 	mov    %rcx,0x140(%rsp)
  e6a28b:	00
  e6a28c:	48 89 9c 24 38 01 00 	mov    %rbx,0x138(%rsp)
  e6a293:	00
  e6a294:	4c 8b 60 38          	mov    0x38(%rax),%r12
  e6a298:	4c 89 64 24 30       	mov    %r12,0x30(%rsp)
  e6a29d:	4c 8b 68 30          	mov    0x30(%rax),%r13
  e6a2a1:	4c 89 ac 24 f8 00 00 	mov    %r13,0xf8(%rsp)
  e6a2a8:	00
  e6a2a9:	45 31 d2             	xor    %r10d,%r10d
  e6a2ac:	e9 fe 00 00 00       	jmp    e6a3af <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x1af>
  e6a2b1:	48 89 5c 24 50       	mov    %rbx,0x50(%rsp)
  e6a2b6:	48 89 4c 24 58       	mov    %rcx,0x58(%rsp)
  e6a2bb:	48 8d 35 23 3d 41 00 	lea    0x413d23(%rip),%rsi        # 127dfe5 <go:string.*+0x547d>
  e6a2c2:	48 89 74 24 70       	mov    %rsi,0x70(%rsp)
  e6a2c7:	48 c7 44 24 78 08 00 	movq   $0x8,0x78(%rsp)
  e6a2ce:	00 00
  e6a2d0:	48 8b 54 24 60       	mov    0x60(%rsp),%rdx
  e6a2d5:	48 8b 7c 24 68       	mov    0x68(%rsp),%rdi
  e6a2da:	4c 8b 8c 24 80 00 00 	mov    0x80(%rsp),%r9
  e6a2e1:	00
  e6a2e2:	4c 8b 94 24 88 00 00 	mov    0x88(%rsp),%r10
  e6a2e9:	00
  e6a2ea:	4c 8b 9c 24 90 00 00 	mov    0x90(%rsp),%r11
  e6a2f1:	00
  e6a2f2:	48 89 d8             	mov    %rbx,%rax
  e6a2f5:	48 89 cb             	mov    %rcx,%rbx
  e6a2f8:	48 89 d1             	mov    %rdx,%rcx
  e6a2fb:	41 b8 08 00 00 00    	mov    $0x8,%r8d
  e6a301:	48 81 c4 00 01 00 00 	add    $0x100,%rsp
  e6a308:	5d                   	pop    %rbp
  e6a309:	c3                   	ret
  e6a30a:	48 89 5c 24 50       	mov    %rbx,0x50(%rsp)
  e6a30f:	48 89 4c 24 58       	mov    %rcx,0x58(%rsp)
  e6a314:	48 8d 35 3d 24 41 00 	lea    0x41243d(%rip),%rsi        # 127c758 <go:string.*+0x3bf0>
  e6a31b:	48 89 74 24 70       	mov    %rsi,0x70(%rsp)
  e6a320:	48 c7 44 24 78 07 00 	movq   $0x7,0x78(%rsp)
  e6a327:	00 00
  e6a329:	48 8b 54 24 60       	mov    0x60(%rsp),%rdx
  e6a32e:	48 8b 7c 24 68       	mov    0x68(%rsp),%rdi
  e6a333:	4c 8b 8c 24 80 00 00 	mov    0x80(%rsp),%r9
  e6a33a:	00
  e6a33b:	4c 8b 94 24 88 00 00 	mov    0x88(%rsp),%r10
  e6a342:	00
  e6a343:	4c 8b 9c 24 90 00 00 	mov    0x90(%rsp),%r11
  e6a34a:	00
  e6a34b:	48 89 d8             	mov    %rbx,%rax
  e6a34e:	48 89 cb             	mov    %rcx,%rbx
  e6a351:	48 89 d1             	mov    %rdx,%rcx
  e6a354:	41 b8 07 00 00 00    	mov    $0x7,%r8d
  e6a35a:	48 81 c4 00 01 00 00 	add    $0x100,%rsp
  e6a361:	5d                   	pop    %rbp
  e6a362:	c3                   	ret
  e6a363:	4c 8b 54 24 48       	mov    0x48(%rsp),%r10
  e6a368:	49 ff c2             	inc    %r10
  e6a36b:	48 8b 84 24 30 01 00 	mov    0x130(%rsp),%rax
  e6a372:	00
  e6a373:	48 8b 8c 24 40 01 00 	mov    0x140(%rsp),%rcx
  e6a37a:	00
  e6a37b:	48 8d 54 24 50       	lea    0x50(%rsp),%rdx
  e6a380:	48 8b 9c 24 38 01 00 	mov    0x138(%rsp),%rbx
  e6a387:	00
  e6a388:	48 8b 74 24 38       	mov    0x38(%rsp),%rsi
  e6a38d:	48 8b bc 24 48 01 00 	mov    0x148(%rsp),%rdi
  e6a394:	00
  e6a395:	4c 8b 44 24 40       	mov    0x40(%rsp),%r8
  e6a39a:	4c 8b 8c 24 b8 00 00 	mov    0xb8(%rsp),%r9
  e6a3a1:	00
  e6a3a2:	4c 8b 64 24 30       	mov    0x30(%rsp),%r12
  e6a3a7:	4c 8b ac 24 f8 00 00 	mov    0xf8(%rsp),%r13
  e6a3ae:	00
  e6a3af:	4d 39 e2             	cmp    %r12,%r10
  e6a3b2:	0f 8d 4f 06 00 00    	jge    e6aa07 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x807>
  e6a3b8:	4c 89 54 24 48       	mov    %r10,0x48(%rsp)
  e6a3bd:	4b 8b 74 d5 00       	mov    0x0(%r13,%r10,8),%rsi
  e6a3c2:	48 89 b4 24 b0 00 00 	mov    %rsi,0xb0(%rsp)
  e6a3c9:	00
  e6a3ca:	48 8b 84 24 10 01 00 	mov    0x110(%rsp),%rax
  e6a3d1:	00
  e6a3d2:	48 8b 9c 24 18 01 00 	mov    0x118(%rsp),%rbx
  e6a3d9:	00
  e6a3da:	48 8b 8c 24 20 01 00 	mov    0x120(%rsp),%rcx
  e6a3e1:	00
  e6a3e2:	48 8b bc 24 28 01 00 	mov    0x128(%rsp),%rdi
  e6a3e9:	00
  e6a3ea:	e8 31 64 00 00       	call   e70820 <github.com/DataDog/dd-trace-go/v2/openfeature.experimentationExclusion.excludes>
  e6a3ef:	84 c0                	test   %al,%al
  e6a3f1:	0f 85 6c ff ff ff    	jne    e6a363 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x163>
  e6a3f7:	48 8b 84 24 b0 00 00 	mov    0xb0(%rsp),%rax
  e6a3fe:	00
  e6a3ff:	48 8b 9c 24 48 01 00 	mov    0x148(%rsp),%rbx
  e6a406:	00
  e6a407:	48 8b 4c 24 38       	mov    0x38(%rsp),%rcx
  e6a40c:	48 8b 7c 24 40       	mov    0x40(%rsp),%rdi
  e6a411:	48 8b b4 24 b8 00 00 	mov    0xb8(%rsp),%rsi
  e6a418:	00
  e6a419:	e8 a2 0d 00 00       	call   e6b1c0 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateAllocation>
  e6a41e:	66 90                	xchg   %ax,%ax
  e6a420:	48 85 c9             	test   %rcx,%rcx
  e6a423:	0f 85 4b 05 00 00    	jne    e6a974 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x774>
  e6a429:	84 db                	test   %bl,%bl
  e6a42b:	0f 84 32 ff ff ff    	je     e6a363 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x163>
  e6a431:	48 85 c0             	test   %rax,%rax
  e6a434:	0f 84 29 ff ff ff    	je     e6a363 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x163>
  e6a43a:	48 89 84 24 a0 00 00 	mov    %rax,0xa0(%rsp)
  e6a441:	00
  e6a442:	48 8b 94 24 30 01 00 	mov    0x130(%rsp),%rdx
  e6a449:	00
  e6a44a:	48 8b 5a 28          	mov    0x28(%rdx),%rbx
  e6a44e:	48 8b 48 18          	mov    0x18(%rax),%rcx
  e6a452:	48 8b 78 20          	mov    0x20(%rax),%rdi
  e6a456:	48 8d 05 a3 35 28 00 	lea    0x2835a3(%rip),%rax        # 10eda00 <runtime.rodata+0x15c9e0>
  e6a45d:	0f 1f 00             	nopl   (%rax)
  e6a460:	e8 1b db 5a ff       	call   417f80 <runtime.mapaccess2_faststr>
  e6a465:	84 db                	test   %bl,%bl
  e6a467:	0f 84 ec 03 00 00    	je     e6a859 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x659>
  e6a46d:	48 8b 10             	mov    (%rax),%rdx
  e6a470:	48 89 94 24 98 00 00 	mov    %rdx,0x98(%rsp)
  e6a477:	00
  e6a478:	48 8b 42 10          	mov    0x10(%rdx),%rax
  e6a47c:	48 8b 5a 18          	mov    0x18(%rdx),%rbx
  e6a480:	48 8b 94 24 30 01 00 	mov    0x130(%rsp),%rdx
  e6a487:	00
  e6a488:	48 8b 4a 18          	mov    0x18(%rdx),%rcx
  e6a48c:	48 8b 7a 20          	mov    0x20(%rdx),%rdi
  e6a490:	e8 2b 26 00 00       	call   e6cac0 <github.com/DataDog/dd-trace-go/v2/openfeature.validateVariantType>
  e6a495:	48 85 c0             	test   %rax,%rax
  e6a498:	0f 84 36 01 00 00    	je     e6a5d4 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x3d4>
  e6a49e:	48 8d 8c 24 c0 00 00 	lea    0xc0(%rsp),%rcx
  e6a4a5:	00
  e6a4a6:	44 0f 11 39          	movups %xmm15,(%rcx)
  e6a4aa:	44 0f 11 79 10       	movups %xmm15,0x10(%rcx)
  e6a4af:	48 8b 15 fa 1d eb 00 	mov    0xeb1dfa(%rip),%rdx        # 1d1c2b0 <github.com/DataDog/dd-trace-go/v2/openfeature.errParseError>
  e6a4b6:	48 85 d2             	test   %rdx,%rdx
  e6a4b9:	74 09                	je     e6a4c4 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x2c4>
  e6a4bb:	48 8b 52 08          	mov    0x8(%rdx),%rdx
  e6a4bf:	48 85 c0             	test   %rax,%rax
  e6a4c2:	eb 03                	jmp    e6a4c7 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x2c7>
  e6a4c4:	48 85 c0             	test   %rax,%rax
  e6a4c7:	4c 8b 05 ea 1d eb 00 	mov    0xeb1dea(%rip),%r8        # 1d1c2b8 <github.com/DataDog/dd-trace-go/v2/openfeature.errParseError+0x8>
  e6a4ce:	48 89 94 24 c0 00 00 	mov    %rdx,0xc0(%rsp)
  e6a4d5:	00
  e6a4d6:	4c 89 84 24 c8 00 00 	mov    %r8,0xc8(%rsp)
  e6a4dd:	00
  e6a4de:	66 90                	xchg   %ax,%ax
  e6a4e0:	74 04                	je     e6a4e6 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x2e6>
  e6a4e2:	48 8b 40 08          	mov    0x8(%rax),%rax
  e6a4e6:	48 89 84 24 d0 00 00 	mov    %rax,0xd0(%rsp)
  e6a4ed:	00
  e6a4ee:	48 89 9c 24 d8 00 00 	mov    %rbx,0xd8(%rsp)
  e6a4f5:	00
  e6a4f6:	48 8d 05 fc 62 43 00 	lea    0x4362fc(%rip),%rax        # 12a07f9 <go:string.*+0x27c91>
  e6a4fd:	bb 1d 00 00 00       	mov    $0x1d,%ebx
  e6a502:	bf 02 00 00 00       	mov    $0x2,%edi
  e6a507:	48 89 fe             	mov    %rdi,%rsi
  e6a50a:	e8 f1 9d 6b ff       	call   524300 <fmt.errorf>
  e6a50f:	48 85 c0             	test   %rax,%rax
  e6a512:	75 2d                	jne    e6a541 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x341>
  e6a514:	90                   	nop
  e6a515:	48 8d 05 a4 5e 29 00 	lea    0x295ea4(%rip),%rax        # 11003c0 <runtime.rodata+0x16f3a0>
  e6a51c:	0f 1f 40 00          	nopl   0x0(%rax)
  e6a520:	e8 db e1 5b ff       	call   428700 <runtime.newobject>
  e6a525:	48 c7 40 08 1d 00 00 	movq   $0x1d,0x8(%rax)
  e6a52c:	00
  e6a52d:	48 8d 0d c5 62 43 00 	lea    0x4362c5(%rip),%rcx        # 12a07f9 <go:string.*+0x27c91>
  e6a534:	48 89 08             	mov    %rcx,(%rax)
  e6a537:	48 89 c3             	mov    %rax,%rbx
  e6a53a:	48 8d 05 9f dc 49 00 	lea    0x49dc9f(%rip),%rax        # 13081e0 <go:itab.*errors.errorString,error>
  e6a541:	48 8d 54 24 50       	lea    0x50(%rsp),%rdx
  e6a546:	44 0f 11 3a          	movups %xmm15,(%rdx)
  e6a54a:	44 0f 11 7a 10       	movups %xmm15,0x10(%rdx)
  e6a54f:	44 0f 11 7a 20       	movups %xmm15,0x20(%rdx)
  e6a554:	44 0f 11 7a 30       	movups %xmm15,0x30(%rdx)
  e6a559:	44 0f 11 7a 38       	movups %xmm15,0x38(%rdx)
  e6a55e:	48 8b 94 24 38 01 00 	mov    0x138(%rsp),%rdx
  e6a565:	00
  e6a566:	48 89 54 24 50       	mov    %rdx,0x50(%rsp)
  e6a56b:	48 8b 94 24 40 01 00 	mov    0x140(%rsp),%rdx
  e6a572:	00
  e6a573:	48 89 54 24 58       	mov    %rdx,0x58(%rsp)
  e6a578:	48 8d 35 89 fa 40 00 	lea    0x40fa89(%rip),%rsi        # 127a008 <go:string.*+0x14a0>
  e6a57f:	48 89 74 24 70       	mov    %rsi,0x70(%rsp)
  e6a584:	48 c7 44 24 78 05 00 	movq   $0x5,0x78(%rsp)
  e6a58b:	00 00
  e6a58d:	48 89 84 24 80 00 00 	mov    %rax,0x80(%rsp)
  e6a594:	00
  e6a595:	48 89 9c 24 88 00 00 	mov    %rbx,0x88(%rsp)
  e6a59c:	00
  e6a59d:	48 8b 54 24 50       	mov    0x50(%rsp),%rdx
  e6a5a2:	4c 8b 64 24 58       	mov    0x58(%rsp),%r12
  e6a5a7:	48 8b 4c 24 60       	mov    0x60(%rsp),%rcx
  e6a5ac:	48 8b 7c 24 68       	mov    0x68(%rsp),%rdi
  e6a5b1:	4c 8b 9c 24 90 00 00 	mov    0x90(%rsp),%r11
  e6a5b8:	00
  e6a5b9:	41 b8 05 00 00 00    	mov    $0x5,%r8d
  e6a5bf:	49 89 c1             	mov    %rax,%r9
  e6a5c2:	49 89 da             	mov    %rbx,%r10
  e6a5c5:	48 89 d0             	mov    %rdx,%rax
  e6a5c8:	4c 89 e3             	mov    %r12,%rbx
  e6a5cb:	48 81 c4 00 01 00 00 	add    $0x100,%rsp
  e6a5d2:	5d                   	pop    %rbp
  e6a5d3:	c3                   	ret
  e6a5d4:	e8 47 43 62 ff       	call   48e920 <runtime.makemap_small>
  e6a5d9:	48 89 84 24 a8 00 00 	mov    %rax,0xa8(%rsp)
  e6a5e0:	00
  e6a5e1:	48 8b 84 24 b0 00 00 	mov    0xb0(%rsp),%rax
  e6a5e8:	00
  e6a5e9:	48 8b 08             	mov    (%rax),%rcx
  e6a5ec:	48 8b 58 08          	mov    0x8(%rax),%rbx
  e6a5f0:	48 89 c8             	mov    %rcx,%rax
  e6a5f3:	e8 48 3a 62 ff       	call   48e040 <runtime.convTstring>
  e6a5f8:	48 89 84 24 f0 00 00 	mov    %rax,0xf0(%rsp)
  e6a5ff:	00
  e6a600:	48 8d 05 79 33 28 00 	lea    0x283379(%rip),%rax        # 10ed980 <runtime.rodata+0x15c960>
  e6a607:	48 8b 9c 24 a8 00 00 	mov    0xa8(%rsp),%rbx
  e6a60e:	00
  e6a60f:	48 8d 0d 64 fb 41 00 	lea    0x41fb64(%rip),%rcx        # 128a17a <go:string.*+0x11612>
  e6a616:	bf 11 00 00 00       	mov    $0x11,%edi
  e6a61b:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
  e6a620:	e8 1b dc 5a ff       	call   418240 <runtime.mapassign_faststr>
  e6a625:	48 8d 0d 94 98 1d 00 	lea    0x1d9894(%rip),%rcx        # 1043ec0 <runtime.rodata+0xb2ea0>
  e6a62c:	48 89 08             	mov    %rcx,(%rax)
  e6a62f:	83 3d 2a 6c 06 01 00 	cmpl   $0x0,0x1066c2a(%rip)        # 1ed1260 <runtime.writeBarrier>
  e6a636:	75 0a                	jne    e6a642 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x442>
  e6a638:	48 8b b4 24 f0 00 00 	mov    0xf0(%rsp),%rsi
  e6a63f:	00
  e6a640:	eb 18                	jmp    e6a65a <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x45a>
  e6a642:	48 8b 50 08          	mov    0x8(%rax),%rdx
  e6a646:	e8 b5 eb 62 ff       	call   499200 <runtime.gcWriteBarrier2>
  e6a64b:	48 8b b4 24 f0 00 00 	mov    0xf0(%rsp),%rsi
  e6a652:	00
  e6a653:	49 89 33             	mov    %rsi,(%r11)
  e6a656:	49 89 53 08          	mov    %rdx,0x8(%r11)
  e6a65a:	48 89 70 08          	mov    %rsi,0x8(%rax)
  e6a65e:	48 8b 94 24 b0 00 00 	mov    0xb0(%rsp),%rdx
  e6a665:	00
  e6a666:	48 8b 72 60          	mov    0x60(%rdx),%rsi
  e6a66a:	48 85 f6             	test   %rsi,%rsi
  e6a66d:	74 05                	je     e6a674 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x474>
  e6a66f:	0f b6 36             	movzbl (%rsi),%esi
  e6a672:	eb 05                	jmp    e6a679 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x479>
  e6a674:	be 01 00 00 00       	mov    $0x1,%esi
  e6a679:	40 88 74 24 2f       	mov    %sil,0x2f(%rsp)
  e6a67e:	48 8d 05 fb 32 28 00 	lea    0x2832fb(%rip),%rax        # 10ed980 <runtime.rodata+0x15c960>
  e6a685:	48 8b 9c 24 a8 00 00 	mov    0xa8(%rsp),%rbx
  e6a68c:	00
  e6a68d:	48 8d 0d 87 76 41 00 	lea    0x417687(%rip),%rcx        # 1281d1b <go:string.*+0x91b3>
  e6a694:	bf 0b 00 00 00       	mov    $0xb,%edi
  e6a699:	e8 a2 db 5a ff       	call   418240 <runtime.mapassign_faststr>
  e6a69e:	48 8d 15 1b 9c 1d 00 	lea    0x1d9c1b(%rip),%rdx        # 10442c0 <runtime.rodata+0xb32a0>
  e6a6a5:	48 89 10             	mov    %rdx,(%rax)
  e6a6a8:	0f b6 54 24 2f       	movzbl 0x2f(%rsp),%edx
  e6a6ad:	0f b6 d2             	movzbl %dl,%edx
  e6a6b0:	48 8d 35 e9 d9 4d 00 	lea    0x4dd9e9(%rip),%rsi        # 13480a0 <runtime.staticuint64s>
  e6a6b7:	48 8d 14 d6          	lea    (%rsi,%rdx,8),%rdx
  e6a6bb:	83 3d 9e 6b 06 01 00 	cmpl   $0x0,0x1066b9e(%rip)        # 1ed1260 <runtime.writeBarrier>
  e6a6c2:	74 0c                	je     e6a6d0 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x4d0>
  e6a6c4:	4c 8b 60 08          	mov    0x8(%rax),%r12
  e6a6c8:	e8 13 eb 62 ff       	call   4991e0 <runtime.gcWriteBarrier1>
  e6a6cd:	4d 89 23             	mov    %r12,(%r11)
  e6a6d0:	48 89 50 08          	mov    %rdx,0x8(%rax)
  e6a6d4:	48 8b 94 24 a0 00 00 	mov    0xa0(%rsp),%rdx
  e6a6db:	00
  e6a6dc:	4c 8b 62 28          	mov    0x28(%rdx),%r12
  e6a6e0:	4d 85 e4             	test   %r12,%r12
  e6a6e3:	74 72                	je     e6a757 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x557>
  e6a6e5:	41 8b 04 24          	mov    (%r12),%eax
  e6a6e9:	e8 72 a2 5b ff       	call   424960 <runtime.convT32>
  e6a6ee:	48 89 84 24 f0 00 00 	mov    %rax,0xf0(%rsp)
  e6a6f5:	00
  e6a6f6:	48 8d 05 83 32 28 00 	lea    0x283283(%rip),%rax        # 10ed980 <runtime.rodata+0x15c960>
  e6a6fd:	48 8b 9c 24 a8 00 00 	mov    0xa8(%rsp),%rbx
  e6a704:	00
  e6a705:	48 8d 0d 8c 4a 42 00 	lea    0x424a8c(%rip),%rcx        # 128f198 <go:string.*+0x16630>
  e6a70c:	bf 14 00 00 00       	mov    $0x14,%edi
  e6a711:	e8 2a db 5a ff       	call   418240 <runtime.mapassign_faststr>
  e6a716:	48 8d 0d 23 99 1d 00 	lea    0x1d9923(%rip),%rcx        # 1044040 <runtime.rodata+0xb3020>
  e6a71d:	48 89 08             	mov    %rcx,(%rax)
  e6a720:	83 3d 39 6b 06 01 00 	cmpl   $0x0,0x1066b39(%rip)        # 1ed1260 <runtime.writeBarrier>
  e6a727:	75 0a                	jne    e6a733 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x533>
  e6a729:	4c 8b a4 24 f0 00 00 	mov    0xf0(%rsp),%r12
  e6a730:	00
  e6a731:	eb 18                	jmp    e6a74b <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x54b>
  e6a733:	48 8b 50 08          	mov    0x8(%rax),%rdx
  e6a737:	e8 c4 ea 62 ff       	call   499200 <runtime.gcWriteBarrier2>
  e6a73c:	4c 8b a4 24 f0 00 00 	mov    0xf0(%rsp),%r12
  e6a743:	00
  e6a744:	4d 89 23             	mov    %r12,(%r11)
  e6a747:	49 89 53 08          	mov    %rdx,0x8(%r11)
  e6a74b:	4c 89 60 08          	mov    %r12,0x8(%rax)
  e6a74f:	48 8b 94 24 a0 00 00 	mov    0xa0(%rsp),%rdx
  e6a756:	00
  e6a757:	4c 8b a4 24 b0 00 00 	mov    0xb0(%rsp),%r12
  e6a75e:	00
  e6a75f:	49 83 7c 24 18 00    	cmpq   $0x0,0x18(%r12)
  e6a765:	74 0e                	je     e6a775 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x575>
  e6a767:	b8 0f 00 00 00       	mov    $0xf,%eax
  e6a76c:	48 8d 0d 19 ca 41 00 	lea    0x41ca19(%rip),%rcx        # 128718c <go:string.*+0xe624>
  e6a773:	eb 4e                	jmp    e6a7c3 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x5c3>
  e6a775:	49 83 7c 24 28 00    	cmpq   $0x0,0x28(%r12)
  e6a77b:	75 08                	jne    e6a785 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x585>
  e6a77d:	49 83 7c 24 30 00    	cmpq   $0x0,0x30(%r12)
  e6a783:	74 1d                	je     e6a7a2 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x5a2>
  e6a785:	49 83 7c 24 50 01    	cmpq   $0x1,0x50(%r12)
  e6a78b:	75 15                	jne    e6a7a2 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x5a2>
  e6a78d:	48 83 7a 08 00       	cmpq   $0x0,0x8(%rdx)
  e6a792:	75 0e                	jne    e6a7a2 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x5a2>
  e6a794:	b8 07 00 00 00       	mov    $0x7,%eax
  e6a799:	48 8d 0d b8 1f 41 00 	lea    0x411fb8(%rip),%rcx        # 127c758 <go:string.*+0x3bf0>
  e6a7a0:	eb 21                	jmp    e6a7c3 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x5c3>
  e6a7a2:	48 83 7a 08 00       	cmpq   $0x0,0x8(%rdx)
  e6a7a7:	74 0e                	je     e6a7b7 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x5b7>
  e6a7a9:	b8 05 00 00 00       	mov    $0x5,%eax
  e6a7ae:	48 8d 0d 58 f8 40 00 	lea    0x40f858(%rip),%rcx        # 127a00d <go:string.*+0x14a5>
  e6a7b5:	eb 0c                	jmp    e6a7c3 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x5c3>
  e6a7b7:	b8 06 00 00 00       	mov    $0x6,%eax
  e6a7bc:	48 8d 0d f0 08 41 00 	lea    0x4108f0(%rip),%rcx        # 127b0b3 <go:string.*+0x254b>
  e6a7c3:	48 8d 54 24 50       	lea    0x50(%rsp),%rdx
  e6a7c8:	44 0f 11 3a          	movups %xmm15,(%rdx)
  e6a7cc:	44 0f 11 7a 10       	movups %xmm15,0x10(%rdx)
  e6a7d1:	44 0f 11 7a 20       	movups %xmm15,0x20(%rdx)
  e6a7d6:	44 0f 11 7a 30       	movups %xmm15,0x30(%rdx)
  e6a7db:	44 0f 11 7a 38       	movups %xmm15,0x38(%rdx)
  e6a7e0:	48 8b 94 24 98 00 00 	mov    0x98(%rsp),%rdx
  e6a7e7:	00
  e6a7e8:	4c 8b 62 10          	mov    0x10(%rdx),%r12
  e6a7ec:	4c 8b 6a 18          	mov    0x18(%rdx),%r13
  e6a7f0:	4c 89 64 24 50       	mov    %r12,0x50(%rsp)
  e6a7f5:	4c 89 6c 24 58       	mov    %r13,0x58(%rsp)
  e6a7fa:	48 8b 7a 08          	mov    0x8(%rdx),%rdi
  e6a7fe:	48 8b 12             	mov    (%rdx),%rdx
  e6a801:	48 89 54 24 60       	mov    %rdx,0x60(%rsp)
  e6a806:	48 89 7c 24 68       	mov    %rdi,0x68(%rsp)
  e6a80b:	48 89 4c 24 70       	mov    %rcx,0x70(%rsp)
  e6a810:	48 89 44 24 78       	mov    %rax,0x78(%rsp)
  e6a815:	4c 8b 9c 24 a8 00 00 	mov    0xa8(%rsp),%r11
  e6a81c:	00
  e6a81d:	4c 89 9c 24 90 00 00 	mov    %r11,0x90(%rsp)
  e6a824:	00
  e6a825:	48 8b 54 24 50       	mov    0x50(%rsp),%rdx
  e6a82a:	48 8b 5c 24 58       	mov    0x58(%rsp),%rbx
  e6a82f:	4c 8b 64 24 60       	mov    0x60(%rsp),%r12
  e6a834:	4c 8b 8c 24 80 00 00 	mov    0x80(%rsp),%r9
  e6a83b:	00
  e6a83c:	4c 8b 94 24 88 00 00 	mov    0x88(%rsp),%r10
  e6a843:	00
  e6a844:	48 89 ce             	mov    %rcx,%rsi
  e6a847:	49 89 c0             	mov    %rax,%r8
  e6a84a:	48 89 d0             	mov    %rdx,%rax
  e6a84d:	4c 89 e1             	mov    %r12,%rcx
  e6a850:	48 81 c4 00 01 00 00 	add    $0x100,%rsp
  e6a857:	5d                   	pop    %rbp
  e6a858:	c3                   	ret
  e6a859:	44 0f 11 bc 24 e0 00 	movups %xmm15,0xe0(%rsp)
  e6a860:	00 00
  e6a862:	48 8b 8c 24 a0 00 00 	mov    0xa0(%rsp),%rcx
  e6a869:	00
  e6a86a:	48 8b 41 18          	mov    0x18(%rcx),%rax
  e6a86e:	48 8b 59 20          	mov    0x20(%rcx),%rbx
  e6a872:	e8 c9 37 62 ff       	call   48e040 <runtime.convTstring>
  e6a877:	48 8d 0d 42 96 1d 00 	lea    0x1d9642(%rip),%rcx        # 1043ec0 <runtime.rodata+0xb2ea0>
  e6a87e:	48 89 8c 24 e0 00 00 	mov    %rcx,0xe0(%rsp)
  e6a885:	00
  e6a886:	48 89 84 24 e8 00 00 	mov    %rax,0xe8(%rsp)
  e6a88d:	00
  e6a88e:	48 8d 05 36 57 45 00 	lea    0x455736(%rip),%rax        # 12bffcb <go:string.*+0x47463>
  e6a895:	bb 2d 00 00 00       	mov    $0x2d,%ebx
  e6a89a:	48 8d 8c 24 e0 00 00 	lea    0xe0(%rsp),%rcx
  e6a8a1:	00
  e6a8a2:	bf 01 00 00 00       	mov    $0x1,%edi
  e6a8a7:	48 89 fe             	mov    %rdi,%rsi
  e6a8aa:	e8 51 9a 6b ff       	call   524300 <fmt.errorf>
  e6a8af:	48 85 c0             	test   %rax,%rax
  e6a8b2:	75 2d                	jne    e6a8e1 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x6e1>
  e6a8b4:	90                   	nop
  e6a8b5:	48 8d 05 04 5b 29 00 	lea    0x295b04(%rip),%rax        # 11003c0 <runtime.rodata+0x16f3a0>
  e6a8bc:	0f 1f 40 00          	nopl   0x0(%rax)
  e6a8c0:	e8 3b de 5b ff       	call   428700 <runtime.newobject>
  e6a8c5:	48 c7 40 08 2d 00 00 	movq   $0x2d,0x8(%rax)
  e6a8cc:	00
  e6a8cd:	48 8d 0d f7 56 45 00 	lea    0x4556f7(%rip),%rcx        # 12bffcb <go:string.*+0x47463>
  e6a8d4:	48 89 08             	mov    %rcx,(%rax)
  e6a8d7:	48 89 c3             	mov    %rax,%rbx
  e6a8da:	48 8d 05 ff d8 49 00 	lea    0x49d8ff(%rip),%rax        # 13081e0 <go:itab.*errors.errorString,error>
  e6a8e1:	48 8d 54 24 50       	lea    0x50(%rsp),%rdx
  e6a8e6:	44 0f 11 3a          	movups %xmm15,(%rdx)
  e6a8ea:	44 0f 11 7a 10       	movups %xmm15,0x10(%rdx)
  e6a8ef:	44 0f 11 7a 20       	movups %xmm15,0x20(%rdx)
  e6a8f4:	44 0f 11 7a 30       	movups %xmm15,0x30(%rdx)
  e6a8f9:	44 0f 11 7a 38       	movups %xmm15,0x38(%rdx)
  e6a8fe:	48 8b 94 24 38 01 00 	mov    0x138(%rsp),%rdx
  e6a905:	00
  e6a906:	48 89 54 24 50       	mov    %rdx,0x50(%rsp)
  e6a90b:	48 8b 94 24 40 01 00 	mov    0x140(%rsp),%rdx
  e6a912:	00
  e6a913:	48 89 54 24 58       	mov    %rdx,0x58(%rsp)
  e6a918:	48 8d 35 e9 f6 40 00 	lea    0x40f6e9(%rip),%rsi        # 127a008 <go:string.*+0x14a0>
  e6a91f:	48 89 74 24 70       	mov    %rsi,0x70(%rsp)
  e6a924:	48 c7 44 24 78 05 00 	movq   $0x5,0x78(%rsp)
  e6a92b:	00 00
  e6a92d:	48 89 84 24 80 00 00 	mov    %rax,0x80(%rsp)
  e6a934:	00
  e6a935:	48 89 9c 24 88 00 00 	mov    %rbx,0x88(%rsp)
  e6a93c:	00
  e6a93d:	48 8b 54 24 50       	mov    0x50(%rsp),%rdx
  e6a942:	4c 8b 64 24 58       	mov    0x58(%rsp),%r12
  e6a947:	48 8b 4c 24 60       	mov    0x60(%rsp),%rcx
  e6a94c:	48 8b 7c 24 68       	mov    0x68(%rsp),%rdi
  e6a951:	4c 8b 9c 24 90 00 00 	mov    0x90(%rsp),%r11
  e6a958:	00
  e6a959:	41 b8 05 00 00 00    	mov    $0x5,%r8d
  e6a95f:	49 89 c1             	mov    %rax,%r9
  e6a962:	49 89 da             	mov    %rbx,%r10
  e6a965:	48 89 d0             	mov    %rdx,%rax
  e6a968:	4c 89 e3             	mov    %r12,%rbx
  e6a96b:	48 81 c4 00 01 00 00 	add    $0x100,%rsp
  e6a972:	5d                   	pop    %rbp
  e6a973:	c3                   	ret
  e6a974:	48 8d 54 24 50       	lea    0x50(%rsp),%rdx
  e6a979:	44 0f 11 3a          	movups %xmm15,(%rdx)
  e6a97d:	44 0f 11 7a 10       	movups %xmm15,0x10(%rdx)
  e6a982:	44 0f 11 7a 20       	movups %xmm15,0x20(%rdx)
  e6a987:	44 0f 11 7a 30       	movups %xmm15,0x30(%rdx)
  e6a98c:	44 0f 11 7a 38       	movups %xmm15,0x38(%rdx)
  e6a991:	48 8b 94 24 38 01 00 	mov    0x138(%rsp),%rdx
  e6a998:	00
  e6a999:	48 89 54 24 50       	mov    %rdx,0x50(%rsp)
  e6a99e:	48 8b 94 24 40 01 00 	mov    0x140(%rsp),%rdx
  e6a9a5:	00
  e6a9a6:	48 89 54 24 58       	mov    %rdx,0x58(%rsp)
  e6a9ab:	48 8d 35 56 f6 40 00 	lea    0x40f656(%rip),%rsi        # 127a008 <go:string.*+0x14a0>
  e6a9b2:	48 89 74 24 70       	mov    %rsi,0x70(%rsp)
  e6a9b7:	48 c7 44 24 78 05 00 	movq   $0x5,0x78(%rsp)
  e6a9be:	00 00
  e6a9c0:	48 89 8c 24 80 00 00 	mov    %rcx,0x80(%rsp)
  e6a9c7:	00
  e6a9c8:	48 89 bc 24 88 00 00 	mov    %rdi,0x88(%rsp)
  e6a9cf:	00
  e6a9d0:	48 8b 44 24 50       	mov    0x50(%rsp),%rax
  e6a9d5:	48 8b 5c 24 58       	mov    0x58(%rsp),%rbx
  e6a9da:	48 8b 54 24 60       	mov    0x60(%rsp),%rdx
  e6a9df:	4c 8b 64 24 68       	mov    0x68(%rsp),%r12
  e6a9e4:	4c 8b 9c 24 90 00 00 	mov    0x90(%rsp),%r11
  e6a9eb:	00
  e6a9ec:	41 b8 05 00 00 00    	mov    $0x5,%r8d
  e6a9f2:	49 89 c9             	mov    %rcx,%r9
  e6a9f5:	49 89 fa             	mov    %rdi,%r10
  e6a9f8:	48 89 d1             	mov    %rdx,%rcx
  e6a9fb:	4c 89 e7             	mov    %r12,%rdi
  e6a9fe:	48 81 c4 00 01 00 00 	add    $0x100,%rsp
  e6aa05:	5d                   	pop    %rbp
  e6aa06:	c3                   	ret
  e6aa07:	44 0f 11 3a          	movups %xmm15,(%rdx)
  e6aa0b:	44 0f 11 7a 10       	movups %xmm15,0x10(%rdx)
  e6aa10:	44 0f 11 7a 20       	movups %xmm15,0x20(%rdx)
  e6aa15:	44 0f 11 7a 30       	movups %xmm15,0x30(%rdx)
  e6aa1a:	44 0f 11 7a 38       	movups %xmm15,0x38(%rdx)
  e6aa1f:	48 8b 54 24 60       	mov    0x60(%rsp),%rdx
  e6aa24:	4c 8b 94 24 88 00 00 	mov    0x88(%rsp),%r10
  e6aa2b:	00
  e6aa2c:	4c 8b 9c 24 90 00 00 	mov    0x90(%rsp),%r11
  e6aa33:	00
  e6aa34:	48 89 5c 24 50       	mov    %rbx,0x50(%rsp)
  e6aa39:	48 89 4c 24 58       	mov    %rcx,0x58(%rsp)
  e6aa3e:	48 8d 35 13 1d 41 00 	lea    0x411d13(%rip),%rsi        # 127c758 <go:string.*+0x3bf0>
  e6aa45:	48 89 74 24 70       	mov    %rsi,0x70(%rsp)
  e6aa4a:	48 c7 44 24 78 07 00 	movq   $0x7,0x78(%rsp)
  e6aa51:	00 00
  e6aa53:	48 89 d8             	mov    %rbx,%rax
  e6aa56:	48 89 cb             	mov    %rcx,%rbx
  e6aa59:	48 89 d1             	mov    %rdx,%rcx
  e6aa5c:	31 ff                	xor    %edi,%edi
  e6aa5e:	41 b8 07 00 00 00    	mov    $0x7,%r8d
  e6aa64:	45 31 c9             	xor    %r9d,%r9d
  e6aa67:	48 81 c4 00 01 00 00 	add    $0x100,%rsp
  e6aa6e:	5d                   	pop    %rbp
  e6aa6f:	c3                   	ret
  e6aa70:	48 89 44 24 28       	mov    %rax,0x28(%rsp)
  e6aa75:	48 89 5c 24 30       	mov    %rbx,0x30(%rsp)
  e6aa7a:	48 89 4c 24 38       	mov    %rcx,0x38(%rsp)
  e6aa7f:	48 89 7c 24 40       	mov    %rdi,0x40(%rsp)
  e6aa84:	48 89 74 24 48       	mov    %rsi,0x48(%rsp)
  e6aa89:	4c 89 44 24 50       	mov    %r8,0x50(%rsp)
  e6aa8e:	4c 89 4c 24 58       	mov    %r9,0x58(%rsp)
  e6aa93:	e8 68 cc 62 ff       	call   497700 <runtime.morestack_noctxt.abi0>
  e6aa98:	48 8b 44 24 28       	mov    0x28(%rsp),%rax
  e6aa9d:	48 8b 5c 24 30       	mov    0x30(%rsp),%rbx
  e6aaa2:	48 8b 4c 24 38       	mov    0x38(%rsp),%rcx
  e6aaa7:	48 8b 7c 24 40       	mov    0x40(%rsp),%rdi
  e6aaac:	48 8b 74 24 48       	mov    0x48(%rsp),%rsi
  e6aab1:	4c 8b 44 24 50       	mov    0x50(%rsp),%r8
  e6aab6:	4c 8b 4c 24 58       	mov    0x58(%rsp),%r9
  e6aabb:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
  e6aac0:	e9 3b f7 ff ff       	jmp    e6a200 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag>

Disassembly of section .fini:
