from django.db.models import signals
from django.db import models, connection, transaction


def update_tree(instance, sender, **kwargs):
        """
        Updates all tree data.
        """

        sql = """
        WITH RECURSIVE pagetree AS
            (
                SELECT id, parent_id, 0 AS level,
                    ARRAY[position] AS position_array,
                    ARRAY[]::text[] AS slug_array,
                    ARRAY[id] AS id_array
                FROM %(db_table)s
                WHERE parent_id IS NULL
                UNION ALL
                SELECT page.id, page.parent_id, parent.level + 1 as level,
                    parent.position_array || ARRAY[page.position] AS position_array,
                    parent.slug_array || ARRAY[CAST(page.slug as TEXT)] AS slug_array,
                    parent.id_array || ARRAY[page.id] AS id_array
                FROM %(db_table)s AS page
                JOIN
                pagetree AS parent
                ON (page.parent_id = parent.id)
            )
            SELECT
                id,
                CASE WHEN level=0 THEN '/'
                     ELSE '/' || array_to_string(slug_array, '/') || '/'
                END AS url,
                level,
                id_array,
                position_array INTO TEMP _pagetmp
            FROM pagetree;
        UPDATE %(db_table)s SET
            url = _pagetmp.url,
            level = _pagetmp.level,
            id_array = _pagetmp.id_array,
            position_array = _pagetmp.position_array FROM _pagetmp
        WHERE %(db_table)s.id = _pagetmp.id;
        DROP TABLE _pagetmp;
        """ % {'db_table': sender._meta.db_table}
        cursor = connection.cursor()
        cursor.execute(sql)
        transaction.commit_unless_managed()


def register(model):
    signals.post_save.connect(update_tree, sender=model)
    signals.post_delete.connect(update_tree, sender=model)

