import json

from hyp.responder import Responder
from fixtures import PostResponder, PostSerializer, CommentResponder


def test_one_to_many():
    comments = [
        {'id': 1, 'content': 'My comment'},
        {'id': 2, 'content': 'Another comment'},
    ]
    post = {'id': 1, 'title': 'My title', 'comments': comments}

    data = PostResponder().respond(post, links=['comments'])

    assert json.loads(data) == {
        'posts': [
            {
                'id': 1,
                'title': 'My title',
                'links': {
                    'comments': [1, 2],
                }
            },
        ],
        'links': {
            'posts.comments': {
                'href': 'http://example.com/comments/{posts.comments}',
                'type': 'comments',
            }
        }
    }


def test_one_to_one():
    author = {'id': 1}
    post = {'id': 1, 'title': 'My title', 'author': author}

    data = PostResponder().respond(post, links=['author'])

    assert json.loads(data) == {
        'posts': [
            {
                'id': 1,
                'title': 'My title',
                'links': {
                    'author': 1,
                }
            },
        ],
        'links': {
            'posts.author': {
                'href': 'http://example.com/people/{posts.author}',
                'type': 'people',
            }
        }
    }


def test_without_href():
    class MyPostResponder(Responder):
        TYPE = 'post'
        SERIALIZER = PostSerializer
        LINKS = {
            'comments': {'responder': CommentResponder()},
        }

    comments = [
        {'id': 1, 'content': 'My comment'},
        {'id': 2, 'content': 'Another comment'},
    ]
    post = {'id': 1, 'title': 'My title', 'comments': comments}

    data = MyPostResponder().respond(post, links=['comments'])

    assert json.loads(data) == {
        'posts': [
            {
                'id': 1,
                'title': 'My title',
                'links': {
                    'comments': [1, 2],
                }
            },
        ],
        'links': {
            'posts.comments': {
                'type': 'comments',
            }
        }
    }
