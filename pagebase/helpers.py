from django.db import connection, transaction
from django.db.models import signals


def update_tree(instance, sender, **kwargs):
        """
        Updates all tree data.

        Correct a pages section to always match the parents section. There are
        still many things that can go wrong such as defining yourself as
        parent. Using the same section for multiple nodes
        on level 1 etc.
        """

        sql = """
        WITH RECURSIVE pagetree AS
            (
                SELECT id, section, parent_id, 1 AS level,
                    ARRAY[position] AS position_array,
                    ARRAY[slug]::text[] AS slug_array,
                    ARRAY[id] AS id_array
                FROM %(db_table)s
                WHERE parent_id IS NULL
                UNION ALL
                SELECT page.id, parent.section, page.parent_id, parent.level + 1 as level,
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
                section,
                '/' || array_to_string(slug_array, '/') || '/' AS url,
                level,
                id_array,
                position_array
            INTO TEMP _pagetmp FROM pagetree;
        UPDATE %(db_table)s SET
            section = _pagetmp.section,
            url = _pagetmp.url,
            level = _pagetmp.level,
            id_array = _pagetmp.id_array,
            position_array = _pagetmp.position_array
        FROM _pagetmp WHERE %(db_table)s.id = _pagetmp.id;
        DROP TABLE _pagetmp;
        """ % {'db_table': sender._meta.db_table}
        cursor = connection.cursor()
        cursor.execute(sql)
        transaction.commit_unless_managed()


def register(model):
    # attach listeners to update tree
    signals.post_save.connect(update_tree, sender=model)
    signals.post_delete.connect(update_tree, sender=model)

