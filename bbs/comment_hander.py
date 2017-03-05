#!/usr/bin/env python
# -*- coding:utf-8 -*-

def add_node(tree_dic, comment):
    if comment.parent_comment is None:
        tree_dic[comment] = {}
    else:
        for k, v in tree_dic.items():
            if k == comment.parent_comment:
                tree_dic[comment.parent_comment][comment] = {}
            else:
                add_node(v, comment)


def render_tree_node(tree_dic, margin_val, parent_key):
    html = ""
    for k, v in tree_dic.items():
        ele = "<div class='child-comment child-comment-sm' " + \
              "style='margin-left:%spx;display:block;word-break: break-all;word-wrap: break-word;'>" % margin_val + \
              "<span class='comment-node-text'>%s</span>" % k.user.name + \
              "<span style='margin-left:5px'>回复</span>" + \
              "<span class='comment-node-text'>%s</span>" % parent_key.user.name + \
              ':' + "<span style='margin-left:5px'>%s</span>" % k.comment + \
              "<span style='margin-left:20px'>%s </span>" % str(k.date).split('.')[0] + \
              "<span comment-id=%s" % k.id + \
              " style='margin-left:20px' class='glyphicon glyphicon-comment add-comment' ></span></div>"
        html += ele
        html += render_tree_node(v, margin_val + 16, k)
    return html


def render_comment_tree(tree_dic):
    html = ""
    for k, v in tree_dic.items():
        ele = "<div class='child-comment child-comment-sm'" + \
              "style='display:block;word-break: break-all;word-wrap: break-word;' >" + \
              "<span class='comment-node-text'>%s</span>" % k.user.name + \
              ':' + "<span style='margin-left:5px'>%s</span>" % k.comment + \
              "<span style='margin-left:20px'>%s</span>" % str(k.date).split('.')[0] + \
              "<span comment-id='%s'" % k.id + \
              "style='margin-left:20px' class='glyphicon glyphicon-comment add-comment' ></span></div>"
        html += ele
        html += render_tree_node(v, 10, k)
    return html


def build_tree(comment_set):
    tree_dic = {}
    for comment in comment_set:
        add_node(tree_dic, comment)
    return tree_dic
