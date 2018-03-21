package coreapi_test

import (
	"bytes"
	"context"
	"encoding/base64"
	"io"
	"math"
	"strings"
	"testing"

	core "github.com/ipfs/go-ipfs/core"
	coreapi "github.com/ipfs/go-ipfs/core/coreapi"
	coreiface "github.com/ipfs/go-ipfs/core/coreapi/interface"
	coreunix "github.com/ipfs/go-ipfs/core/coreunix"
	keystore "github.com/ipfs/go-ipfs/keystore"
	mdag "github.com/ipfs/go-ipfs/merkledag"
	repo "github.com/ipfs/go-ipfs/repo"
	config "github.com/ipfs/go-ipfs/repo/config"
	ds2 "github.com/ipfs/go-ipfs/thirdparty/datastore2"
	unixfs "github.com/ipfs/go-ipfs/unixfs"

	cbor "gx/ipfs/QmNRz7BDWfdFNVLt7AVvmRefkrURD25EeoipcXqo6yoXU1/go-ipld-cbor"
	peer "gx/ipfs/QmZoWKhxUmZ2seW4BzX6fJkNR8hh9PsGModr7q171yq2SS/go-libp2p-peer"
	ci "gx/ipfs/QmaPbCnUMBohSGo3KnxEa2bHqyJVVeEEcwtqJAYxerieBo/go-libp2p-crypto"
)

const testPeerID = "QmTFauExutTsy4XP6JbMFcw2Wa9645HJt2bTqL6qYDCKfe"

// `echo -n 'hello, world!' | ipfs add`
var hello = coreapi.ResolvedPath("/ipfs/QmQy2Dw4Wk7rdJKjThjYXzfFJNaRKRHhHP5gHHXroJMYxk", nil, nil)
var helloStr = "hello, world!"

// `ipfs object new unixfs-dir`
var emptyDir = coreapi.ResolvedPath("/ipfs/QmUNLLsPACCz1vLxQVkXqqLX5R1X345qqfHbsf67hvA3Nn", nil, nil)

// `echo -n | ipfs add`
var emptyFile = coreapi.ResolvedPath("/ipfs/QmbFMke1KXqnYyBBWxB74N4c5SBnJMVAiMNRcGu6x1AwQH", nil, nil)

func makeAPIIdent(ctx context.Context, fullIdentity bool) (*core.IpfsNode, coreiface.CoreAPI, error) {
	var ident config.Identity
	if fullIdentity {
		sk, pk, err := ci.GenerateKeyPair(ci.RSA, 512)
		if err != nil {
			return nil, nil, err
		}

		id, err := peer.IDFromPublicKey(pk)
		if err != nil {
			return nil, nil, err
		}

		kbytes, err := sk.Bytes()
		if err != nil {
			return nil, nil, err
		}

		ident = config.Identity{
			PeerID:  id.Pretty(),
			PrivKey: base64.StdEncoding.EncodeToString(kbytes),
		}
	} else {
		ident = config.Identity{
			PeerID: testPeerID,
		}
	}

	r := &repo.Mock{
		C: config.Config{
			Identity: ident,
		},
		D: ds2.ThreadSafeCloserMapDatastore(),
		K: keystore.NewMemKeystore(),
	}
	node, err := core.NewNode(ctx, &core.BuildCfg{Repo: r})
	if err != nil {
		return nil, nil, err
	}
	api := coreapi.NewCoreAPI(node)
	return node, api, nil
}

func makeAPI(ctx context.Context) (*core.IpfsNode, coreiface.CoreAPI, error) {
	return makeAPIIdent(ctx, false)
}

func TestAdd(t *testing.T) {
	ctx := context.Background()
	_, api, err := makeAPI(ctx)
	if err != nil {
		t.Error(err)
	}

	str := strings.NewReader(helloStr)
	p, err := api.Unixfs().Add(ctx, str)
	if err != nil {
		t.Error(err)
	}

	if p.String() != hello.String() {
		t.Fatalf("expected path %s, got: %s", hello, p)
	}

	r, err := api.Unixfs().Cat(ctx, hello)
	if err != nil {
		t.Fatal(err)
	}
	buf := make([]byte, len(helloStr))
	_, err = io.ReadFull(r, buf)
	if err != nil {
		t.Error(err)
	}

	if string(buf) != helloStr {
		t.Fatalf("expected [%s], got [%s] [err=%s]", helloStr, string(buf), err)
	}
}

func TestAddEmptyFile(t *testing.T) {
	ctx := context.Background()
	_, api, err := makeAPI(ctx)
	if err != nil {
		t.Error(err)
	}

	str := strings.NewReader("")
	p, err := api.Unixfs().Add(ctx, str)
	if err != nil {
		t.Error(err)
	}

	if p.String() != emptyFile.String() {
		t.Fatalf("expected path %s, got: %s", hello, p)
	}
}

func TestCatBasic(t *testing.T) {
	ctx := context.Background()
	node, api, err := makeAPI(ctx)
	if err != nil {
		t.Fatal(err)
	}

	hr := strings.NewReader(helloStr)
	p, err := coreunix.Add(node, hr)
	if err != nil {
		t.Fatal(err)
	}
	p = "/ipfs/" + p

	if p != hello.String() {
		t.Fatalf("expected CID %s, got: %s", hello, p)
	}

	r, err := api.Unixfs().Cat(ctx, hello)
	if err != nil {
		t.Fatal(err)
	}

	buf := make([]byte, len(helloStr))
	_, err = io.ReadFull(r, buf)
	if err != nil {
		t.Error(err)
	}
	if string(buf) != helloStr {
		t.Fatalf("expected [%s], got [%s] [err=%s]", helloStr, string(buf), err)
	}
}

func TestCatEmptyFile(t *testing.T) {
	ctx := context.Background()
	node, api, err := makeAPI(ctx)
	if err != nil {
		t.Fatal(err)
	}

	_, err = coreunix.Add(node, strings.NewReader(""))
	if err != nil {
		t.Fatal(err)
	}

	r, err := api.Unixfs().Cat(ctx, emptyFile)
	if err != nil {
		t.Fatal(err)
	}

	buf := make([]byte, 1) // non-zero so that Read() actually tries to read
	n, err := io.ReadFull(r, buf)
	if err != nil && err != io.EOF {
		t.Error(err)
	}
	if !bytes.HasPrefix(buf, []byte{0x00}) {
		t.Fatalf("expected empty data, got [%s] [read=%d]", buf, n)
	}
}

func TestCatDir(t *testing.T) {
	ctx := context.Background()
	node, api, err := makeAPI(ctx)
	if err != nil {
		t.Error(err)
	}
	edir := unixfs.EmptyDirNode()
	err = node.DAG.Add(ctx, edir)
	if err != nil {
		t.Error(err)
	}
	p := coreapi.ParseCid(edir.Cid())

	if p.String() != emptyDir.String() {
		t.Fatalf("expected path %s, got: %s", emptyDir, p)
	}

	_, err = api.Unixfs().Cat(ctx, emptyDir)
	if err != coreiface.ErrIsDir {
		t.Fatalf("expected ErrIsDir, got: %s", err)
	}
}

func TestCatNonUnixfs(t *testing.T) {
	ctx := context.Background()
	node, api, err := makeAPI(ctx)
	if err != nil {
		t.Error(err)
	}

	nd := new(mdag.ProtoNode)
	err = node.DAG.Add(ctx, nd)
	if err != nil {
		t.Error(err)
	}

	_, err = api.Unixfs().Cat(ctx, coreapi.ParseCid(nd.Cid()))
	if !strings.Contains(err.Error(), "proto: required field") {
		t.Fatalf("expected protobuf error, got: %s", err)
	}
}

func TestCatOffline(t *testing.T) {
	ctx := context.Background()
	_, api, err := makeAPI(ctx)
	if err != nil {
		t.Error(err)
	}

	_, err = api.Unixfs().Cat(ctx, coreapi.ResolvedPath("/ipns/Qmfoobar", nil, nil))
	if err != coreiface.ErrOffline {
		t.Fatalf("expected ErrOffline, got: %s", err)
	}
}

func TestLs(t *testing.T) {
	ctx := context.Background()
	node, api, err := makeAPI(ctx)
	if err != nil {
		t.Error(err)
	}

	r := strings.NewReader("content-of-file")
	k, _, err := coreunix.AddWrapped(node, r, "name-of-file")
	if err != nil {
		t.Error(err)
	}
	parts := strings.Split(k, "/")
	if len(parts) != 2 {
		t.Errorf("unexpected path: %s", k)
	}
	p := coreapi.ResolvedPath("/ipfs/"+parts[0], nil, nil)

	links, err := api.Unixfs().Ls(ctx, p)
	if err != nil {
		t.Error(err)
	}

	if len(links) != 1 {
		t.Fatalf("expected 1 link, got %d", len(links))
	}
	if links[0].Size != 23 {
		t.Fatalf("expected size = 23, got %d", links[0].Size)
	}
	if links[0].Name != "name-of-file" {
		t.Fatalf("expected name = name-of-file, got %s", links[0].Name)
	}
	if links[0].Cid.String() != "QmX3qQVKxDGz3URVC3861Z3CKtQKGBn6ffXRBBWGMFz9Lr" {
		t.Fatalf("expected cid = QmX3qQVKxDGz3URVC3861Z3CKtQKGBn6ffXRBBWGMFz9Lr, got %s", links[0].Cid)
	}
}

func TestLsEmptyDir(t *testing.T) {
	ctx := context.Background()
	node, api, err := makeAPI(ctx)
	if err != nil {
		t.Error(err)
	}

	err = node.DAG.Add(ctx, unixfs.EmptyDirNode())
	if err != nil {
		t.Error(err)
	}

	links, err := api.Unixfs().Ls(ctx, emptyDir)
	if err != nil {
		t.Error(err)
	}

	if len(links) != 0 {
		t.Fatalf("expected 0 links, got %d", len(links))
	}
}

// TODO(lgierth) this should test properly, with len(links) > 0
func TestLsNonUnixfs(t *testing.T) {
	ctx := context.Background()
	node, api, err := makeAPI(ctx)
	if err != nil {
		t.Error(err)
	}

	nd, err := cbor.WrapObject(map[string]interface{}{"foo": "bar"}, math.MaxUint64, -1)
	if err != nil {
		t.Fatal(err)
	}

	err = node.DAG.Add(ctx, nd)
	if err != nil {
		t.Error(err)
	}

	links, err := api.Unixfs().Ls(ctx, coreapi.ParseCid(nd.Cid()))
	if err != nil {
		t.Error(err)
	}

	if len(links) != 0 {
		t.Fatalf("expected 0 links, got %d", len(links))
	}
}
