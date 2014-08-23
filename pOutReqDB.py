#!/usr/bin/env python

import json
import decimal
import psycopg2
import psycopg2.extras
import os
import sys

def insert_row():
	sql_insert = ('INSERT INTO items (%s) VALUES (%s)' %
	              (','.join('%s' % k for k in item_dict.keys()),','.join('%%(%s)s' % k for k in item_dict.keys())))

	#print(simple_cursor.mogrify(sql_insert, item_dict))

	try:
		dict_cursor.execute(sql_insert, item_dict)
		db.commit()

	except Exception as e:
		print(e)

def get_row(get_item):
	sql_get = ("SELECT * FROM items WHERE item_no = ('%s')" % get_item)

	#print(dict_cursor.mogrify(sql_get, get_item))

	try:
		dict_cursor.execute(sql_get)
		row = dict_cursor.fetchone()
		return row

	except Exception as e:
		print(e)

def delete_row(del_item):
	sql_delete = ('DELETE FROM items WHERE item_no = %s' % del_item)

	#print(simple_cursor.mogrify(sql_delete, del_item))

	try:
		simple_cursor.execute(sql_delete)
		db.commit()

	except Exception as e:
		print(e)

def check_for_item(chk_item):
#    print("item we're checking for:", chk_item)
	sql_check = ("SELECT count(*) from items where item_no = (%s)" % chk_item)
	simple_cursor.execute(sql_check)
	return simple_cursor.fetchone()[0]

def check_for_changes():

	change_count = 0

	#print()
	for k, v in item_dict.iteritems():
		if str(item[k]) == str(item_dict[k]) or item[k] == item_dict[k]:
			pass
		else:
			print("key %s, item value %s, item_dict value %s" % (k, item[k], item_dict[k]))
			change_count += 1
	if change_count > 0:
		print("account: %s\n" % (item_dict['bill_to_id']))

	return change_count

def create_items_table(table_name):
	print("create table: ", table_name)
	sql_create_table = ("CREATE TABLE %s (seq_no           mediumint not null auto_increment,\
                                    payload                 varchar(36),\
                                    timestamp                 varchar(36),\
                                    version               varchar(6),\
                                    mfg_item_id            varchar(22),\
                                    class_code_1           varchar(6),\
                                    class_code_2           varchar(6),\
                                    class_code_3           varchar(6),\
                                    class_code_4           varchar(6),\
                                    season_code_1          varchar(6),\
                                    season_code_2          varchar(6),\
                                    season_code_3          varchar(6),\
                                    season_code_4          varchar(6),\
                                    type_flag              varchar(1),\
                                    disc_flag              varchar(1),\
                                    spec_ord_flag          varchar(1),\
                                    taxable_flag           varchar(1),\
                                    serial_no_flag         varchar(1),\
                                    user_code_1            varchar(6),\
                                    user_code_2            varchar(6),\
                                    user_code_3            varchar(6),\
                                    user_code_4            varchar(6),\
                                    sell_uofm              varchar(6),\
                                    alt_uofm_flag          varchar(1),\
                                    xfer_uofm              varchar(6),\
                                    xfer_std_pack          integer,\
                                    qty_dec_places         integer,\
                                    list_prc               numeric(9,3),\
                                    sell_prc               numeric(9,3),\
                                    sell_prc_2             numeric(9,3),\
                                    sell_prc_3             numeric(9,3),\
                                    min_prc                numeric(9,3),\
                                    unit_cost              numeric(10,4),\
                                    avg_cost               numeric(10,4),\
                                    std_cost               numeric(10,4),\
                                    last_cost              numeric(10,4),\
                                    inv_cost               numeric(10,4),\
                                    inventory_acct         integer,\
                                    sales_acct             integer,\
                                    cogs_acct              integer,\
                                    entry_date             timestamp,\
                                    entry_by               varchar(6),\
                                    update_date            timestamp,\
                                    update_by              varchar(6),\
                                    discontinued_date      timestamp,\
                                    remove_date            timestamp,\
                                    rplc_item_no           integer,\
                                    xfer_uofm_sell_units   numeric(8,4),\
                                    purch_flag             varchar(1),\
                                    web_export_flag        varchar(1),\
                                    purch_uofm             varchar(6),\
                                    purch_uofm_sell_units  numeric(8,4),\
                                    alt_purch_uofm_flag    varchar(1),\
                                    qty_cost_flag          varchar(1),\
                                    purch_std_pack         integer,\
                                    avg_lead_days          numeric(4,1),\
                                    purch_cost             numeric(10,4),\
                                    barcode                varchar(18),\
                                    stat_flag              varchar(1),\
                                    barcode_type           varchar(1),\
                                    update_level           integer,\
                                    isbn                   varchar(13),\
                                    prc_labels_flag        varchar(1),\
                                    req_flag               varchar(1),\
                                    dspl_stat_flag         varchar(2),\
                                    desc_user_flag         varchar(1),\
                                    store_xfer_flag        varchar(1),\
                                    save_taxable_flag      varchar(1),\
                                    special_handling_flag  varchar(2),\
	                                db_sync_timestamp      timestamp)" % table_name)

	simple_cursor.execute(sql_create_table)
	db.commit()

db = psycopg2.connect(host='192.168.51.137', database='sumit01', user='sumit')
dict_cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
simple_cursor = db.cursor()

new_table='pOutReq'
simple_cursor.execute("select exists(select 1 from information_schema.tables where table_name = %s)", (new_table,))
have_table = simple_cursor.fetchone()[0]
if have_table:
	print('db table exists:', have_table)
else:
#    print('db table exists:', have_table)
#    print("try to create table: ", new_table)
	create_items_table(new_table)


eof = "N"
i = 0
j = 0
k = 0

#python3:
items_json = open('data/export/items001.json', encoding='utf-8')
#python2:
#items_json = open('/u/sumit8/export/items001.json')
while (eof != "Y"):
	i += 1
	try:
		a_line = items_json.readline()
		if len(a_line) != 0:
			k += 1
			good_dict = "Y"
			if k > 4999:
				k = 0
				print(i)

			try:
				item_dict = json.loads(a_line)
			except:
				print(i, a_line[1:19])
				good_dict = "N"

			if good_dict == "Y":
				j += 1
#			if check_for_item(item_dict['item_no']):
#				delete_row(item_dict['item_no'])
#                    errorcodes.lookup(e.pgcode[:2])
#                    print("deleted:", item_dict['item_no'])
#			else:
#                    print("insert item = ", item_dict['item_no'])
#				insert_row()

				item = get_row(item_dict['item_no'])
				#rsg = raw_input("after get_row press <enter>")
				if item:
					#print('item rec found, check for changes')
					if check_for_changes() > 0:
						#print("change count = ", check_for_changes())
						#rsg = raw_input("press <enter>")
						delete_row(item_dict['item_no'])
						#print("insert item = ", item_dict['item_no'])
						insert_row()
						update_count += 1
				else:
					#print("insert item = ", item_dict['item_no'])
					#rsg = raw_input("press <enter>")
					insert_row()
					add_count += 1


	except:
		print(i, a_line)
		break

	if len(a_line) == 0:
		print('\nend of file')
		eof = "Y"


items_json.close()

print('\njson objects processed: %s' % j)

dict_cursor.close()
db.close()
print('\nDone')