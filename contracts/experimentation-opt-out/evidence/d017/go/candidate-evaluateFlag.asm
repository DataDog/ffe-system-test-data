
/tmp/d017-go-evidence/candidate.test:     file format elf64-x86-64


Disassembly of section .init:

Disassembly of section .plt:

Disassembly of section .text:

0000000000e6a200 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag>:
  e6a200:	4c 8d a4 24 78 ff ff 	lea    -0x88(%rsp),%r12
  e6a207:	ff
  e6a208:	4d 3b 66 10          	cmp    0x10(%r14),%r12
  e6a20c:	0f 86 cb 08 00 00    	jbe    e6aadd <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x8dd>
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
  e6a255:	0f 84 b7 00 00 00    	je     e6a312 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x112>
  e6a25b:	80 78 10 00          	cmpb   $0x0,0x10(%rax)
  e6a25f:	90                   	nop
  e6a260:	74 57                	je     e6a2b9 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0xb9>
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
  e6a2a9:	4c 8b bc 24 10 01 00 	mov    0x110(%rsp),%r15
  e6a2b0:	00
  e6a2b1:	45 31 d2             	xor    %r10d,%r10d
  e6a2b4:	e9 ba 00 00 00       	jmp    e6a373 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x173>
  e6a2b9:	48 89 5c 24 50       	mov    %rbx,0x50(%rsp)
  e6a2be:	48 89 4c 24 58       	mov    %rcx,0x58(%rsp)
  e6a2c3:	48 8d 35 1b 3d 41 00 	lea    0x413d1b(%rip),%rsi        # 127dfe5 <go:string.*+0x547d>
  e6a2ca:	48 89 74 24 70       	mov    %rsi,0x70(%rsp)
  e6a2cf:	48 c7 44 24 78 08 00 	movq   $0x8,0x78(%rsp)
  e6a2d6:	00 00
  e6a2d8:	48 8b 54 24 60       	mov    0x60(%rsp),%rdx
  e6a2dd:	48 8b 7c 24 68       	mov    0x68(%rsp),%rdi
  e6a2e2:	4c 8b 8c 24 80 00 00 	mov    0x80(%rsp),%r9
  e6a2e9:	00
  e6a2ea:	4c 8b 94 24 88 00 00 	mov    0x88(%rsp),%r10
  e6a2f1:	00
  e6a2f2:	4c 8b 9c 24 90 00 00 	mov    0x90(%rsp),%r11
  e6a2f9:	00
  e6a2fa:	48 89 d8             	mov    %rbx,%rax
  e6a2fd:	48 89 cb             	mov    %rcx,%rbx
  e6a300:	48 89 d1             	mov    %rdx,%rcx
  e6a303:	41 b8 08 00 00 00    	mov    $0x8,%r8d
  e6a309:	48 81 c4 00 01 00 00 	add    $0x100,%rsp
  e6a310:	5d                   	pop    %rbp
  e6a311:	c3                   	ret
  e6a312:	48 89 5c 24 50       	mov    %rbx,0x50(%rsp)
  e6a317:	48 89 4c 24 58       	mov    %rcx,0x58(%rsp)
  e6a31c:	48 8d 35 35 24 41 00 	lea    0x412435(%rip),%rsi        # 127c758 <go:string.*+0x3bf0>
  e6a323:	48 89 74 24 70       	mov    %rsi,0x70(%rsp)
  e6a328:	48 c7 44 24 78 07 00 	movq   $0x7,0x78(%rsp)
  e6a32f:	00 00
  e6a331:	48 8b 54 24 60       	mov    0x60(%rsp),%rdx
  e6a336:	48 8b 7c 24 68       	mov    0x68(%rsp),%rdi
  e6a33b:	4c 8b 8c 24 80 00 00 	mov    0x80(%rsp),%r9
  e6a342:	00
  e6a343:	4c 8b 94 24 88 00 00 	mov    0x88(%rsp),%r10
  e6a34a:	00
  e6a34b:	4c 8b 9c 24 90 00 00 	mov    0x90(%rsp),%r11
  e6a352:	00
  e6a353:	48 89 d8             	mov    %rbx,%rax
  e6a356:	48 89 cb             	mov    %rcx,%rbx
  e6a359:	48 89 d1             	mov    %rdx,%rcx
  e6a35c:	41 b8 07 00 00 00    	mov    $0x7,%r8d
  e6a362:	48 81 c4 00 01 00 00 	add    $0x100,%rsp
  e6a369:	5d                   	pop    %rbp
  e6a36a:	c3                   	ret
  e6a36b:	49 ff c2             	inc    %r10
  e6a36e:	48 8d 54 24 50       	lea    0x50(%rsp),%rdx
  e6a373:	4d 39 e2             	cmp    %r12,%r10
  e6a376:	0f 8d f8 06 00 00    	jge    e6aa74 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x874>
  e6a37c:	4c 89 54 24 48       	mov    %r10,0x48(%rsp)
  e6a381:	4f 8b 5c d5 00       	mov    0x0(%r13,%r10,8),%r11
  e6a386:	4c 89 9c 24 b0 00 00 	mov    %r11,0xb0(%rsp)
  e6a38d:	00
  e6a38e:	4d 85 ff             	test   %r15,%r15
  e6a391:	75 12                	jne    e6a3a5 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x1a5>
  e6a393:	31 d2                	xor    %edx,%edx
  e6a395:	88 54 24 2f          	mov    %dl,0x2f(%rsp)
  e6a399:	48 8d 54 24 50       	lea    0x50(%rsp),%rdx
  e6a39e:	66 90                	xchg   %ax,%ax
  e6a3a0:	e9 80 00 00 00       	jmp    e6a425 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x225>
  e6a3a5:	4c 89 f8             	mov    %r15,%rax
  e6a3a8:	48 8b 9c 24 18 01 00 	mov    0x118(%rsp),%rbx
  e6a3af:	00
  e6a3b0:	48 8b 8c 24 20 01 00 	mov    0x120(%rsp),%rcx
  e6a3b7:	00
  e6a3b8:	48 8b bc 24 28 01 00 	mov    0x128(%rsp),%rdi
  e6a3bf:	00
  e6a3c0:	4c 89 de             	mov    %r11,%rsi
  e6a3c3:	e8 b8 64 00 00       	call   e70880 <github.com/DataDog/dd-trace-go/v2/openfeature.experimentationExclusion.excludes>
  e6a3c8:	48 8b 8c 24 40 01 00 	mov    0x140(%rsp),%rcx
  e6a3cf:	00
  e6a3d0:	48 8d 54 24 50       	lea    0x50(%rsp),%rdx
  e6a3d5:	48 8b 9c 24 38 01 00 	mov    0x138(%rsp),%rbx
  e6a3dc:	00
  e6a3dd:	48 8b 74 24 38       	mov    0x38(%rsp),%rsi
  e6a3e2:	48 8b bc 24 48 01 00 	mov    0x148(%rsp),%rdi
  e6a3e9:	00
  e6a3ea:	4c 8b 44 24 40       	mov    0x40(%rsp),%r8
  e6a3ef:	4c 8b 8c 24 b8 00 00 	mov    0xb8(%rsp),%r9
  e6a3f6:	00
  e6a3f7:	4c 8b 54 24 48       	mov    0x48(%rsp),%r10
  e6a3fc:	4c 8b 9c 24 b0 00 00 	mov    0xb0(%rsp),%r11
  e6a403:	00
  e6a404:	4c 8b 64 24 30       	mov    0x30(%rsp),%r12
  e6a409:	4c 8b ac 24 f8 00 00 	mov    0xf8(%rsp),%r13
  e6a410:	00
  e6a411:	4c 8b bc 24 10 01 00 	mov    0x110(%rsp),%r15
  e6a418:	00
  e6a419:	88 44 24 2f          	mov    %al,0x2f(%rsp)
  e6a41d:	48 8b 84 24 30 01 00 	mov    0x130(%rsp),%rax
  e6a424:	00
  e6a425:	0f b6 54 24 2f       	movzbl 0x2f(%rsp),%edx
  e6a42a:	84 d2                	test   %dl,%dl
  e6a42c:	0f 85 39 ff ff ff    	jne    e6a36b <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x16b>
  e6a432:	4c 89 d8             	mov    %r11,%rax
  e6a435:	48 89 fb             	mov    %rdi,%rbx
  e6a438:	48 89 f1             	mov    %rsi,%rcx
  e6a43b:	4c 89 c7             	mov    %r8,%rdi
  e6a43e:	4c 89 ce             	mov    %r9,%rsi
  e6a441:	e8 da 0d 00 00       	call   e6b220 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateAllocation>
  e6a446:	48 85 c9             	test   %rcx,%rcx
  e6a449:	0f 85 92 05 00 00    	jne    e6a9e1 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x7e1>
  e6a44f:	84 db                	test   %bl,%bl
  e6a451:	74 05                	je     e6a458 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x258>
  e6a453:	48 85 c0             	test   %rax,%rax
  e6a456:	75 51                	jne    e6a4a9 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x2a9>
  e6a458:	48 8b 84 24 30 01 00 	mov    0x130(%rsp),%rax
  e6a45f:	00
  e6a460:	48 8b 8c 24 40 01 00 	mov    0x140(%rsp),%rcx
  e6a467:	00
  e6a468:	48 8b 9c 24 38 01 00 	mov    0x138(%rsp),%rbx
  e6a46f:	00
  e6a470:	48 8b 74 24 38       	mov    0x38(%rsp),%rsi
  e6a475:	48 8b bc 24 48 01 00 	mov    0x148(%rsp),%rdi
  e6a47c:	00
  e6a47d:	4c 8b 44 24 40       	mov    0x40(%rsp),%r8
  e6a482:	4c 8b 8c 24 b8 00 00 	mov    0xb8(%rsp),%r9
  e6a489:	00
  e6a48a:	4c 8b 54 24 48       	mov    0x48(%rsp),%r10
  e6a48f:	4c 8b 64 24 30       	mov    0x30(%rsp),%r12
  e6a494:	4c 8b ac 24 f8 00 00 	mov    0xf8(%rsp),%r13
  e6a49b:	00
  e6a49c:	4c 8b bc 24 10 01 00 	mov    0x110(%rsp),%r15
  e6a4a3:	00
  e6a4a4:	e9 c2 fe ff ff       	jmp    e6a36b <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x16b>
  e6a4a9:	48 89 84 24 a0 00 00 	mov    %rax,0xa0(%rsp)
  e6a4b0:	00
  e6a4b1:	48 8b 94 24 30 01 00 	mov    0x130(%rsp),%rdx
  e6a4b8:	00
  e6a4b9:	48 8b 5a 28          	mov    0x28(%rdx),%rbx
  e6a4bd:	48 8b 48 18          	mov    0x18(%rax),%rcx
  e6a4c1:	48 8b 78 20          	mov    0x20(%rax),%rdi
  e6a4c5:	48 8d 05 34 35 28 00 	lea    0x283534(%rip),%rax        # 10eda00 <runtime.rodata+0x15c9e0>
  e6a4cc:	e8 af da 5a ff       	call   417f80 <runtime.mapaccess2_faststr>
  e6a4d1:	84 db                	test   %bl,%bl
  e6a4d3:	0f 84 ef 03 00 00    	je     e6a8c8 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x6c8>
  e6a4d9:	48 8b 10             	mov    (%rax),%rdx
  e6a4dc:	48 89 94 24 98 00 00 	mov    %rdx,0x98(%rsp)
  e6a4e3:	00
  e6a4e4:	48 8b 42 10          	mov    0x10(%rdx),%rax
  e6a4e8:	48 8b 5a 18          	mov    0x18(%rdx),%rbx
  e6a4ec:	48 8b 94 24 30 01 00 	mov    0x130(%rsp),%rdx
  e6a4f3:	00
  e6a4f4:	48 8b 4a 18          	mov    0x18(%rdx),%rcx
  e6a4f8:	48 8b 7a 20          	mov    0x20(%rdx),%rdi
  e6a4fc:	0f 1f 40 00          	nopl   0x0(%rax)
  e6a500:	e8 1b 26 00 00       	call   e6cb20 <github.com/DataDog/dd-trace-go/v2/openfeature.validateVariantType>
  e6a505:	48 85 c0             	test   %rax,%rax
  e6a508:	0f 84 33 01 00 00    	je     e6a641 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x441>
  e6a50e:	48 8d 8c 24 c0 00 00 	lea    0xc0(%rsp),%rcx
  e6a515:	00
  e6a516:	44 0f 11 39          	movups %xmm15,(%rcx)
  e6a51a:	44 0f 11 79 10       	movups %xmm15,0x10(%rcx)
  e6a51f:	48 8b 15 8a 1d eb 00 	mov    0xeb1d8a(%rip),%rdx        # 1d1c2b0 <github.com/DataDog/dd-trace-go/v2/openfeature.errParseError>
  e6a526:	48 85 d2             	test   %rdx,%rdx
  e6a529:	74 09                	je     e6a534 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x334>
  e6a52b:	48 8b 52 08          	mov    0x8(%rdx),%rdx
  e6a52f:	48 85 c0             	test   %rax,%rax
  e6a532:	eb 03                	jmp    e6a537 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x337>
  e6a534:	48 85 c0             	test   %rax,%rax
  e6a537:	4c 8b 05 7a 1d eb 00 	mov    0xeb1d7a(%rip),%r8        # 1d1c2b8 <github.com/DataDog/dd-trace-go/v2/openfeature.errParseError+0x8>
  e6a53e:	48 89 94 24 c0 00 00 	mov    %rdx,0xc0(%rsp)
  e6a545:	00
  e6a546:	4c 89 84 24 c8 00 00 	mov    %r8,0xc8(%rsp)
  e6a54d:	00
  e6a54e:	74 04                	je     e6a554 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x354>
  e6a550:	48 8b 40 08          	mov    0x8(%rax),%rax
  e6a554:	48 89 84 24 d0 00 00 	mov    %rax,0xd0(%rsp)
  e6a55b:	00
  e6a55c:	48 89 9c 24 d8 00 00 	mov    %rbx,0xd8(%rsp)
  e6a563:	00
  e6a564:	48 8d 05 8e 62 43 00 	lea    0x43628e(%rip),%rax        # 12a07f9 <go:string.*+0x27c91>
  e6a56b:	bb 1d 00 00 00       	mov    $0x1d,%ebx
  e6a570:	bf 02 00 00 00       	mov    $0x2,%edi
  e6a575:	48 89 fe             	mov    %rdi,%rsi
  e6a578:	e8 83 9d 6b ff       	call   524300 <fmt.errorf>
  e6a57d:	0f 1f 00             	nopl   (%rax)
  e6a580:	48 85 c0             	test   %rax,%rax
  e6a583:	75 29                	jne    e6a5ae <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x3ae>
  e6a585:	90                   	nop
  e6a586:	48 8d 05 33 5e 29 00 	lea    0x295e33(%rip),%rax        # 11003c0 <runtime.rodata+0x16f3a0>
  e6a58d:	e8 6e e1 5b ff       	call   428700 <runtime.newobject>
  e6a592:	48 c7 40 08 1d 00 00 	movq   $0x1d,0x8(%rax)
  e6a599:	00
  e6a59a:	48 8d 0d 58 62 43 00 	lea    0x436258(%rip),%rcx        # 12a07f9 <go:string.*+0x27c91>
  e6a5a1:	48 89 08             	mov    %rcx,(%rax)
  e6a5a4:	48 89 c3             	mov    %rax,%rbx
  e6a5a7:	48 8d 05 32 dc 49 00 	lea    0x49dc32(%rip),%rax        # 13081e0 <go:itab.*errors.errorString,error>
  e6a5ae:	48 8d 54 24 50       	lea    0x50(%rsp),%rdx
  e6a5b3:	44 0f 11 3a          	movups %xmm15,(%rdx)
  e6a5b7:	44 0f 11 7a 10       	movups %xmm15,0x10(%rdx)
  e6a5bc:	44 0f 11 7a 20       	movups %xmm15,0x20(%rdx)
  e6a5c1:	44 0f 11 7a 30       	movups %xmm15,0x30(%rdx)
  e6a5c6:	44 0f 11 7a 38       	movups %xmm15,0x38(%rdx)
  e6a5cb:	48 8b 94 24 38 01 00 	mov    0x138(%rsp),%rdx
  e6a5d2:	00
  e6a5d3:	48 89 54 24 50       	mov    %rdx,0x50(%rsp)
  e6a5d8:	48 8b 94 24 40 01 00 	mov    0x140(%rsp),%rdx
  e6a5df:	00
  e6a5e0:	48 89 54 24 58       	mov    %rdx,0x58(%rsp)
  e6a5e5:	48 8d 35 1c fa 40 00 	lea    0x40fa1c(%rip),%rsi        # 127a008 <go:string.*+0x14a0>
  e6a5ec:	48 89 74 24 70       	mov    %rsi,0x70(%rsp)
  e6a5f1:	48 c7 44 24 78 05 00 	movq   $0x5,0x78(%rsp)
  e6a5f8:	00 00
  e6a5fa:	48 89 84 24 80 00 00 	mov    %rax,0x80(%rsp)
  e6a601:	00
  e6a602:	48 89 9c 24 88 00 00 	mov    %rbx,0x88(%rsp)
  e6a609:	00
  e6a60a:	48 8b 54 24 50       	mov    0x50(%rsp),%rdx
  e6a60f:	4c 8b 64 24 58       	mov    0x58(%rsp),%r12
  e6a614:	48 8b 4c 24 60       	mov    0x60(%rsp),%rcx
  e6a619:	48 8b 7c 24 68       	mov    0x68(%rsp),%rdi
  e6a61e:	4c 8b 9c 24 90 00 00 	mov    0x90(%rsp),%r11
  e6a625:	00
  e6a626:	41 b8 05 00 00 00    	mov    $0x5,%r8d
  e6a62c:	49 89 c1             	mov    %rax,%r9
  e6a62f:	49 89 da             	mov    %rbx,%r10
  e6a632:	48 89 d0             	mov    %rdx,%rax
  e6a635:	4c 89 e3             	mov    %r12,%rbx
  e6a638:	48 81 c4 00 01 00 00 	add    $0x100,%rsp
  e6a63f:	5d                   	pop    %rbp
  e6a640:	c3                   	ret
  e6a641:	e8 da 42 62 ff       	call   48e920 <runtime.makemap_small>
  e6a646:	48 89 84 24 a8 00 00 	mov    %rax,0xa8(%rsp)
  e6a64d:	00
  e6a64e:	48 8b 84 24 b0 00 00 	mov    0xb0(%rsp),%rax
  e6a655:	00
  e6a656:	48 8b 08             	mov    (%rax),%rcx
  e6a659:	48 8b 58 08          	mov    0x8(%rax),%rbx
  e6a65d:	48 89 c8             	mov    %rcx,%rax
  e6a660:	e8 db 39 62 ff       	call   48e040 <runtime.convTstring>
  e6a665:	48 89 84 24 f0 00 00 	mov    %rax,0xf0(%rsp)
  e6a66c:	00
  e6a66d:	48 8d 05 0c 33 28 00 	lea    0x28330c(%rip),%rax        # 10ed980 <runtime.rodata+0x15c960>
  e6a674:	48 8b 9c 24 a8 00 00 	mov    0xa8(%rsp),%rbx
  e6a67b:	00
  e6a67c:	48 8d 0d f7 fa 41 00 	lea    0x41faf7(%rip),%rcx        # 128a17a <go:string.*+0x11612>
  e6a683:	bf 11 00 00 00       	mov    $0x11,%edi
  e6a688:	e8 b3 db 5a ff       	call   418240 <runtime.mapassign_faststr>
  e6a68d:	48 8d 0d 2c 98 1d 00 	lea    0x1d982c(%rip),%rcx        # 1043ec0 <runtime.rodata+0xb2ea0>
  e6a694:	48 89 08             	mov    %rcx,(%rax)
  e6a697:	83 3d c2 6b 06 01 00 	cmpl   $0x0,0x1066bc2(%rip)        # 1ed1260 <runtime.writeBarrier>
  e6a69e:	66 90                	xchg   %ax,%ax
  e6a6a0:	75 0a                	jne    e6a6ac <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x4ac>
  e6a6a2:	48 8b b4 24 f0 00 00 	mov    0xf0(%rsp),%rsi
  e6a6a9:	00
  e6a6aa:	eb 18                	jmp    e6a6c4 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x4c4>
  e6a6ac:	48 8b 50 08          	mov    0x8(%rax),%rdx
  e6a6b0:	e8 4b eb 62 ff       	call   499200 <runtime.gcWriteBarrier2>
  e6a6b5:	48 8b b4 24 f0 00 00 	mov    0xf0(%rsp),%rsi
  e6a6bc:	00
  e6a6bd:	49 89 33             	mov    %rsi,(%r11)
  e6a6c0:	49 89 53 08          	mov    %rdx,0x8(%r11)
  e6a6c4:	48 89 70 08          	mov    %rsi,0x8(%rax)
  e6a6c8:	48 8b 94 24 b0 00 00 	mov    0xb0(%rsp),%rdx
  e6a6cf:	00
  e6a6d0:	48 8b 72 60          	mov    0x60(%rdx),%rsi
  e6a6d4:	48 85 f6             	test   %rsi,%rsi
  e6a6d7:	74 05                	je     e6a6de <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x4de>
  e6a6d9:	0f b6 36             	movzbl (%rsi),%esi
  e6a6dc:	eb 05                	jmp    e6a6e3 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x4e3>
  e6a6de:	be 01 00 00 00       	mov    $0x1,%esi
  e6a6e3:	40 88 74 24 2e       	mov    %sil,0x2e(%rsp)
  e6a6e8:	48 8d 05 91 32 28 00 	lea    0x283291(%rip),%rax        # 10ed980 <runtime.rodata+0x15c960>
  e6a6ef:	48 8b 9c 24 a8 00 00 	mov    0xa8(%rsp),%rbx
  e6a6f6:	00
  e6a6f7:	48 8d 0d 1d 76 41 00 	lea    0x41761d(%rip),%rcx        # 1281d1b <go:string.*+0x91b3>
  e6a6fe:	bf 0b 00 00 00       	mov    $0xb,%edi
  e6a703:	e8 38 db 5a ff       	call   418240 <runtime.mapassign_faststr>
  e6a708:	48 8d 15 b1 9b 1d 00 	lea    0x1d9bb1(%rip),%rdx        # 10442c0 <runtime.rodata+0xb32a0>
  e6a70f:	48 89 10             	mov    %rdx,(%rax)
  e6a712:	0f b6 54 24 2e       	movzbl 0x2e(%rsp),%edx
  e6a717:	0f b6 d2             	movzbl %dl,%edx
  e6a71a:	48 8d 35 7f d9 4d 00 	lea    0x4dd97f(%rip),%rsi        # 13480a0 <runtime.staticuint64s>
  e6a721:	48 8d 14 d6          	lea    (%rsi,%rdx,8),%rdx
  e6a725:	83 3d 34 6b 06 01 00 	cmpl   $0x0,0x1066b34(%rip)        # 1ed1260 <runtime.writeBarrier>
  e6a72c:	74 0c                	je     e6a73a <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x53a>
  e6a72e:	4c 8b 60 08          	mov    0x8(%rax),%r12
  e6a732:	e8 a9 ea 62 ff       	call   4991e0 <runtime.gcWriteBarrier1>
  e6a737:	4d 89 23             	mov    %r12,(%r11)
  e6a73a:	48 89 50 08          	mov    %rdx,0x8(%rax)
  e6a73e:	48 8b 94 24 a0 00 00 	mov    0xa0(%rsp),%rdx
  e6a745:	00
  e6a746:	4c 8b 62 28          	mov    0x28(%rdx),%r12
  e6a74a:	4d 85 e4             	test   %r12,%r12
  e6a74d:	74 77                	je     e6a7c6 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x5c6>
  e6a74f:	41 8b 04 24          	mov    (%r12),%eax
  e6a753:	e8 08 a2 5b ff       	call   424960 <runtime.convT32>
  e6a758:	48 89 84 24 f0 00 00 	mov    %rax,0xf0(%rsp)
  e6a75f:	00
  e6a760:	48 8d 05 19 32 28 00 	lea    0x283219(%rip),%rax        # 10ed980 <runtime.rodata+0x15c960>
  e6a767:	48 8b 9c 24 a8 00 00 	mov    0xa8(%rsp),%rbx
  e6a76e:	00
  e6a76f:	48 8d 0d 22 4a 42 00 	lea    0x424a22(%rip),%rcx        # 128f198 <go:string.*+0x16630>
  e6a776:	bf 14 00 00 00       	mov    $0x14,%edi
  e6a77b:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
  e6a780:	e8 bb da 5a ff       	call   418240 <runtime.mapassign_faststr>
  e6a785:	48 8d 0d b4 98 1d 00 	lea    0x1d98b4(%rip),%rcx        # 1044040 <runtime.rodata+0xb3020>
  e6a78c:	48 89 08             	mov    %rcx,(%rax)
  e6a78f:	83 3d ca 6a 06 01 00 	cmpl   $0x0,0x1066aca(%rip)        # 1ed1260 <runtime.writeBarrier>
  e6a796:	75 0a                	jne    e6a7a2 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x5a2>
  e6a798:	4c 8b a4 24 f0 00 00 	mov    0xf0(%rsp),%r12
  e6a79f:	00
  e6a7a0:	eb 18                	jmp    e6a7ba <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x5ba>
  e6a7a2:	48 8b 50 08          	mov    0x8(%rax),%rdx
  e6a7a6:	e8 55 ea 62 ff       	call   499200 <runtime.gcWriteBarrier2>
  e6a7ab:	4c 8b a4 24 f0 00 00 	mov    0xf0(%rsp),%r12
  e6a7b2:	00
  e6a7b3:	4d 89 23             	mov    %r12,(%r11)
  e6a7b6:	49 89 53 08          	mov    %rdx,0x8(%r11)
  e6a7ba:	4c 89 60 08          	mov    %r12,0x8(%rax)
  e6a7be:	48 8b 94 24 a0 00 00 	mov    0xa0(%rsp),%rdx
  e6a7c5:	00
  e6a7c6:	4c 8b a4 24 b0 00 00 	mov    0xb0(%rsp),%r12
  e6a7cd:	00
  e6a7ce:	49 83 7c 24 18 00    	cmpq   $0x0,0x18(%r12)
  e6a7d4:	74 0e                	je     e6a7e4 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x5e4>
  e6a7d6:	b8 0f 00 00 00       	mov    $0xf,%eax
  e6a7db:	48 8d 0d aa c9 41 00 	lea    0x41c9aa(%rip),%rcx        # 128718c <go:string.*+0xe624>
  e6a7e2:	eb 4e                	jmp    e6a832 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x632>
  e6a7e4:	49 83 7c 24 28 00    	cmpq   $0x0,0x28(%r12)
  e6a7ea:	75 08                	jne    e6a7f4 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x5f4>
  e6a7ec:	49 83 7c 24 30 00    	cmpq   $0x0,0x30(%r12)
  e6a7f2:	74 1d                	je     e6a811 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x611>
  e6a7f4:	49 83 7c 24 50 01    	cmpq   $0x1,0x50(%r12)
  e6a7fa:	75 15                	jne    e6a811 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x611>
  e6a7fc:	48 83 7a 08 00       	cmpq   $0x0,0x8(%rdx)
  e6a801:	75 0e                	jne    e6a811 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x611>
  e6a803:	b8 07 00 00 00       	mov    $0x7,%eax
  e6a808:	48 8d 0d 49 1f 41 00 	lea    0x411f49(%rip),%rcx        # 127c758 <go:string.*+0x3bf0>
  e6a80f:	eb 21                	jmp    e6a832 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x632>
  e6a811:	48 83 7a 08 00       	cmpq   $0x0,0x8(%rdx)
  e6a816:	74 0e                	je     e6a826 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x626>
  e6a818:	b8 05 00 00 00       	mov    $0x5,%eax
  e6a81d:	48 8d 0d e9 f7 40 00 	lea    0x40f7e9(%rip),%rcx        # 127a00d <go:string.*+0x14a5>
  e6a824:	eb 0c                	jmp    e6a832 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x632>
  e6a826:	b8 06 00 00 00       	mov    $0x6,%eax
  e6a82b:	48 8d 0d 81 08 41 00 	lea    0x410881(%rip),%rcx        # 127b0b3 <go:string.*+0x254b>
  e6a832:	48 8d 54 24 50       	lea    0x50(%rsp),%rdx
  e6a837:	44 0f 11 3a          	movups %xmm15,(%rdx)
  e6a83b:	44 0f 11 7a 10       	movups %xmm15,0x10(%rdx)
  e6a840:	44 0f 11 7a 20       	movups %xmm15,0x20(%rdx)
  e6a845:	44 0f 11 7a 30       	movups %xmm15,0x30(%rdx)
  e6a84a:	44 0f 11 7a 38       	movups %xmm15,0x38(%rdx)
  e6a84f:	48 8b 94 24 98 00 00 	mov    0x98(%rsp),%rdx
  e6a856:	00
  e6a857:	4c 8b 62 10          	mov    0x10(%rdx),%r12
  e6a85b:	4c 8b 6a 18          	mov    0x18(%rdx),%r13
  e6a85f:	4c 89 64 24 50       	mov    %r12,0x50(%rsp)
  e6a864:	4c 89 6c 24 58       	mov    %r13,0x58(%rsp)
  e6a869:	48 8b 7a 08          	mov    0x8(%rdx),%rdi
  e6a86d:	48 8b 12             	mov    (%rdx),%rdx
  e6a870:	48 89 54 24 60       	mov    %rdx,0x60(%rsp)
  e6a875:	48 89 7c 24 68       	mov    %rdi,0x68(%rsp)
  e6a87a:	48 89 4c 24 70       	mov    %rcx,0x70(%rsp)
  e6a87f:	48 89 44 24 78       	mov    %rax,0x78(%rsp)
  e6a884:	4c 8b 9c 24 a8 00 00 	mov    0xa8(%rsp),%r11
  e6a88b:	00
  e6a88c:	4c 89 9c 24 90 00 00 	mov    %r11,0x90(%rsp)
  e6a893:	00
  e6a894:	48 8b 54 24 50       	mov    0x50(%rsp),%rdx
  e6a899:	48 8b 5c 24 58       	mov    0x58(%rsp),%rbx
  e6a89e:	4c 8b 64 24 60       	mov    0x60(%rsp),%r12
  e6a8a3:	4c 8b 8c 24 80 00 00 	mov    0x80(%rsp),%r9
  e6a8aa:	00
  e6a8ab:	4c 8b 94 24 88 00 00 	mov    0x88(%rsp),%r10
  e6a8b2:	00
  e6a8b3:	48 89 ce             	mov    %rcx,%rsi
  e6a8b6:	49 89 c0             	mov    %rax,%r8
  e6a8b9:	48 89 d0             	mov    %rdx,%rax
  e6a8bc:	4c 89 e1             	mov    %r12,%rcx
  e6a8bf:	48 81 c4 00 01 00 00 	add    $0x100,%rsp
  e6a8c6:	5d                   	pop    %rbp
  e6a8c7:	c3                   	ret
  e6a8c8:	44 0f 11 bc 24 e0 00 	movups %xmm15,0xe0(%rsp)
  e6a8cf:	00 00
  e6a8d1:	48 8b 8c 24 a0 00 00 	mov    0xa0(%rsp),%rcx
  e6a8d8:	00
  e6a8d9:	48 8b 41 18          	mov    0x18(%rcx),%rax
  e6a8dd:	48 8b 59 20          	mov    0x20(%rcx),%rbx
  e6a8e1:	e8 5a 37 62 ff       	call   48e040 <runtime.convTstring>
  e6a8e6:	48 8d 0d d3 95 1d 00 	lea    0x1d95d3(%rip),%rcx        # 1043ec0 <runtime.rodata+0xb2ea0>
  e6a8ed:	48 89 8c 24 e0 00 00 	mov    %rcx,0xe0(%rsp)
  e6a8f4:	00
  e6a8f5:	48 89 84 24 e8 00 00 	mov    %rax,0xe8(%rsp)
  e6a8fc:	00
  e6a8fd:	48 8d 05 c7 56 45 00 	lea    0x4556c7(%rip),%rax        # 12bffcb <go:string.*+0x47463>
  e6a904:	bb 2d 00 00 00       	mov    $0x2d,%ebx
  e6a909:	48 8d 8c 24 e0 00 00 	lea    0xe0(%rsp),%rcx
  e6a910:	00
  e6a911:	bf 01 00 00 00       	mov    $0x1,%edi
  e6a916:	48 89 fe             	mov    %rdi,%rsi
  e6a919:	e8 e2 99 6b ff       	call   524300 <fmt.errorf>
  e6a91e:	66 90                	xchg   %ax,%ax
  e6a920:	48 85 c0             	test   %rax,%rax
  e6a923:	75 29                	jne    e6a94e <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag+0x74e>
  e6a925:	90                   	nop
  e6a926:	48 8d 05 93 5a 29 00 	lea    0x295a93(%rip),%rax        # 11003c0 <runtime.rodata+0x16f3a0>
  e6a92d:	e8 ce dd 5b ff       	call   428700 <runtime.newobject>
  e6a932:	48 c7 40 08 2d 00 00 	movq   $0x2d,0x8(%rax)
  e6a939:	00
  e6a93a:	48 8d 0d 8a 56 45 00 	lea    0x45568a(%rip),%rcx        # 12bffcb <go:string.*+0x47463>
  e6a941:	48 89 08             	mov    %rcx,(%rax)
  e6a944:	48 89 c3             	mov    %rax,%rbx
  e6a947:	48 8d 05 92 d8 49 00 	lea    0x49d892(%rip),%rax        # 13081e0 <go:itab.*errors.errorString,error>
  e6a94e:	48 8d 54 24 50       	lea    0x50(%rsp),%rdx
  e6a953:	44 0f 11 3a          	movups %xmm15,(%rdx)
  e6a957:	44 0f 11 7a 10       	movups %xmm15,0x10(%rdx)
  e6a95c:	44 0f 11 7a 20       	movups %xmm15,0x20(%rdx)
  e6a961:	44 0f 11 7a 30       	movups %xmm15,0x30(%rdx)
  e6a966:	44 0f 11 7a 38       	movups %xmm15,0x38(%rdx)
  e6a96b:	48 8b 94 24 38 01 00 	mov    0x138(%rsp),%rdx
  e6a972:	00
  e6a973:	48 89 54 24 50       	mov    %rdx,0x50(%rsp)
  e6a978:	48 8b 94 24 40 01 00 	mov    0x140(%rsp),%rdx
  e6a97f:	00
  e6a980:	48 89 54 24 58       	mov    %rdx,0x58(%rsp)
  e6a985:	48 8d 35 7c f6 40 00 	lea    0x40f67c(%rip),%rsi        # 127a008 <go:string.*+0x14a0>
  e6a98c:	48 89 74 24 70       	mov    %rsi,0x70(%rsp)
  e6a991:	48 c7 44 24 78 05 00 	movq   $0x5,0x78(%rsp)
  e6a998:	00 00
  e6a99a:	48 89 84 24 80 00 00 	mov    %rax,0x80(%rsp)
  e6a9a1:	00
  e6a9a2:	48 89 9c 24 88 00 00 	mov    %rbx,0x88(%rsp)
  e6a9a9:	00
  e6a9aa:	48 8b 54 24 50       	mov    0x50(%rsp),%rdx
  e6a9af:	4c 8b 64 24 58       	mov    0x58(%rsp),%r12
  e6a9b4:	48 8b 4c 24 60       	mov    0x60(%rsp),%rcx
  e6a9b9:	48 8b 7c 24 68       	mov    0x68(%rsp),%rdi
  e6a9be:	4c 8b 9c 24 90 00 00 	mov    0x90(%rsp),%r11
  e6a9c5:	00
  e6a9c6:	41 b8 05 00 00 00    	mov    $0x5,%r8d
  e6a9cc:	49 89 c1             	mov    %rax,%r9
  e6a9cf:	49 89 da             	mov    %rbx,%r10
  e6a9d2:	48 89 d0             	mov    %rdx,%rax
  e6a9d5:	4c 89 e3             	mov    %r12,%rbx
  e6a9d8:	48 81 c4 00 01 00 00 	add    $0x100,%rsp
  e6a9df:	5d                   	pop    %rbp
  e6a9e0:	c3                   	ret
  e6a9e1:	48 8d 54 24 50       	lea    0x50(%rsp),%rdx
  e6a9e6:	44 0f 11 3a          	movups %xmm15,(%rdx)
  e6a9ea:	44 0f 11 7a 10       	movups %xmm15,0x10(%rdx)
  e6a9ef:	44 0f 11 7a 20       	movups %xmm15,0x20(%rdx)
  e6a9f4:	44 0f 11 7a 30       	movups %xmm15,0x30(%rdx)
  e6a9f9:	44 0f 11 7a 38       	movups %xmm15,0x38(%rdx)
  e6a9fe:	48 8b 94 24 38 01 00 	mov    0x138(%rsp),%rdx
  e6aa05:	00
  e6aa06:	48 89 54 24 50       	mov    %rdx,0x50(%rsp)
  e6aa0b:	48 8b 94 24 40 01 00 	mov    0x140(%rsp),%rdx
  e6aa12:	00
  e6aa13:	48 89 54 24 58       	mov    %rdx,0x58(%rsp)
  e6aa18:	48 8d 35 e9 f5 40 00 	lea    0x40f5e9(%rip),%rsi        # 127a008 <go:string.*+0x14a0>
  e6aa1f:	48 89 74 24 70       	mov    %rsi,0x70(%rsp)
  e6aa24:	48 c7 44 24 78 05 00 	movq   $0x5,0x78(%rsp)
  e6aa2b:	00 00
  e6aa2d:	48 89 8c 24 80 00 00 	mov    %rcx,0x80(%rsp)
  e6aa34:	00
  e6aa35:	48 89 bc 24 88 00 00 	mov    %rdi,0x88(%rsp)
  e6aa3c:	00
  e6aa3d:	48 8b 44 24 50       	mov    0x50(%rsp),%rax
  e6aa42:	48 8b 5c 24 58       	mov    0x58(%rsp),%rbx
  e6aa47:	48 8b 54 24 60       	mov    0x60(%rsp),%rdx
  e6aa4c:	4c 8b 64 24 68       	mov    0x68(%rsp),%r12
  e6aa51:	4c 8b 9c 24 90 00 00 	mov    0x90(%rsp),%r11
  e6aa58:	00
  e6aa59:	41 b8 05 00 00 00    	mov    $0x5,%r8d
  e6aa5f:	49 89 c9             	mov    %rcx,%r9
  e6aa62:	49 89 fa             	mov    %rdi,%r10
  e6aa65:	48 89 d1             	mov    %rdx,%rcx
  e6aa68:	4c 89 e7             	mov    %r12,%rdi
  e6aa6b:	48 81 c4 00 01 00 00 	add    $0x100,%rsp
  e6aa72:	5d                   	pop    %rbp
  e6aa73:	c3                   	ret
  e6aa74:	44 0f 11 3a          	movups %xmm15,(%rdx)
  e6aa78:	44 0f 11 7a 10       	movups %xmm15,0x10(%rdx)
  e6aa7d:	44 0f 11 7a 20       	movups %xmm15,0x20(%rdx)
  e6aa82:	44 0f 11 7a 30       	movups %xmm15,0x30(%rdx)
  e6aa87:	44 0f 11 7a 38       	movups %xmm15,0x38(%rdx)
  e6aa8c:	48 8b 54 24 60       	mov    0x60(%rsp),%rdx
  e6aa91:	4c 8b 94 24 88 00 00 	mov    0x88(%rsp),%r10
  e6aa98:	00
  e6aa99:	4c 8b 9c 24 90 00 00 	mov    0x90(%rsp),%r11
  e6aaa0:	00
  e6aaa1:	48 89 5c 24 50       	mov    %rbx,0x50(%rsp)
  e6aaa6:	48 89 4c 24 58       	mov    %rcx,0x58(%rsp)
  e6aaab:	48 8d 35 a6 1c 41 00 	lea    0x411ca6(%rip),%rsi        # 127c758 <go:string.*+0x3bf0>
  e6aab2:	48 89 74 24 70       	mov    %rsi,0x70(%rsp)
  e6aab7:	48 c7 44 24 78 07 00 	movq   $0x7,0x78(%rsp)
  e6aabe:	00 00
  e6aac0:	48 89 d8             	mov    %rbx,%rax
  e6aac3:	48 89 cb             	mov    %rcx,%rbx
  e6aac6:	48 89 d1             	mov    %rdx,%rcx
  e6aac9:	31 ff                	xor    %edi,%edi
  e6aacb:	41 b8 07 00 00 00    	mov    $0x7,%r8d
  e6aad1:	45 31 c9             	xor    %r9d,%r9d
  e6aad4:	48 81 c4 00 01 00 00 	add    $0x100,%rsp
  e6aadb:	5d                   	pop    %rbp
  e6aadc:	c3                   	ret
  e6aadd:	48 89 44 24 28       	mov    %rax,0x28(%rsp)
  e6aae2:	48 89 5c 24 30       	mov    %rbx,0x30(%rsp)
  e6aae7:	48 89 4c 24 38       	mov    %rcx,0x38(%rsp)
  e6aaec:	48 89 7c 24 40       	mov    %rdi,0x40(%rsp)
  e6aaf1:	48 89 74 24 48       	mov    %rsi,0x48(%rsp)
  e6aaf6:	4c 89 44 24 50       	mov    %r8,0x50(%rsp)
  e6aafb:	4c 89 4c 24 58       	mov    %r9,0x58(%rsp)
  e6ab00:	e8 fb cb 62 ff       	call   497700 <runtime.morestack_noctxt.abi0>
  e6ab05:	48 8b 44 24 28       	mov    0x28(%rsp),%rax
  e6ab0a:	48 8b 5c 24 30       	mov    0x30(%rsp),%rbx
  e6ab0f:	48 8b 4c 24 38       	mov    0x38(%rsp),%rcx
  e6ab14:	48 8b 7c 24 40       	mov    0x40(%rsp),%rdi
  e6ab19:	48 8b 74 24 48       	mov    0x48(%rsp),%rsi
  e6ab1e:	4c 8b 44 24 50       	mov    0x50(%rsp),%r8
  e6ab23:	4c 8b 4c 24 58       	mov    0x58(%rsp),%r9
  e6ab28:	e9 d3 f6 ff ff       	jmp    e6a200 <github.com/DataDog/dd-trace-go/v2/openfeature.evaluateFlag>

Disassembly of section .fini:
