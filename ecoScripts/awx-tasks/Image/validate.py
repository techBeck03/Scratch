from awx import AWX
from os import getenv
from pigeon import Pigeon

# ============================================================================
# Global Variables
# ----------------------------------------------------------------------------
pigeon = Pigeon()

# ============================================================================
# Main
# ----------------------------------------------------------------------------

def main():
    try:
        awx = AWX(
            endpoint=getenv('AWX_ENDPOINT'),
            token=getenv('AWX_TOKEN')
        )
        extra_vars = getenv('AWX_WORKFLOW_VARS')
        workflow_tasks = getenv('AWX_WORKFLOW_TASKS')

        resp = awx.validate_deployment_settings(
            awx.render(workflow_tasks), ignore_inventory=False)
        if resp['status'] != 'success':
            pigeon.note.update({
                'status_code': 404,
                'message' : resp['message'],
                'data' : {}
            })
            pigeon.send()
            return
        pigeon.note.update({
            'status_code': 200,
            'message' : resp['message'],
            'data' : {}
        })
        pigeon.send()
        return
    except Exception as e:
        pigeon.note.update({
            'status_code': 400,
            'message' : 'An exception occurred while testing connectivity: {}'.format(str(e)),
            'data' : {}
        })
        pigeon.send()

if __name__ == "__main__":
    main()