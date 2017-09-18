import json
import os
import tempfile
import unittest

import kvservice

class TestKVRest(unittest.TestCase):
    def setUp(self):
        self.fd, self.tempdb = tempfile.mkstemp()
        kvservice.DBFILE = self.tempdb
        self.app = kvservice.app
        self.client = self.app.test_client

    def tearDown(self):
        with kvservice.app.app_context():
            kvservice.close_connection(None)
        os.close(self.fd)
        os.remove(self.tempdb)

    def test_get_empty(self):
        res = self.client().get("/key/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(json.loads(res.data), {})

    def test_add_many_get_all(self):
        cl = self.client()
        D = dict(A="apple", B="ball", C="cat")

        res = cl.put("/key/", data=D)
        self.assertEqual(res.status_code, 201)

        gres = cl.get("/key/")
        self.assertEqual(json.loads(gres.data), D)

    def test_get_one(self):
        cl = self.client()
        cl.put("/key/", data=dict(A="apple", B="ball", C="cat"))
        res = cl.get("/key/B")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(json.loads(res.data), dict(value="ball"))

    def test_add_one(self):
        cl = self.client()
        cl.put("/key/", data=dict(A="apple", B="ball", C="cat"))

        ares = cl.put("/key/D", data=dict(value="DeVito"))
        self.assertEqual(ares.status_code, 201)

        res = cl.get("/key/D")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(json.loads(res.data), dict(value="DeVito"))

    def test_update_one(self):
        cl = self.client()
        cl.put("/key/", data=dict(A="apple", B="ball", C="cat"))

        ures = cl.post("/key/B", data=dict(value="GARBLEDINA!"))
        self.assertEqual(ures.status_code, 202)

        res = cl.get("/key/B")
        self.assertEqual(json.loads(res.data), dict(value="GARBLEDINA!"))

    def test_delete_one(self):
        cl = self.client()
        cl.put("/key/", data=dict(A="apple", B="ball", C="cat"))

        dres = cl.delete("/key/B")
        self.assertEqual(dres.status_code, 204)

        res = cl.get("/key/B")
        self.assertEqual(res.status_code, 204)

if __name__ == "__main__":
    unittest.main()
